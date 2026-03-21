import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import tempfile

from app.models import SourceMatch, SourceResult


SAMPLE_BRIEF = {
    'subject_name': 'Jean Dupont',
    'generated_at': '2026-03-21T14:30:00Z',
    'identity': {
        'full_name': 'Jean Dupont',
        'aliases': ['J. Dupont'],
        'birth_date': '1980-03-15',
        'nationalities': ['French'],
        'addresses': ['10 rue de la Paix, Paris'],
    },
    'corporate_network': [
        {
            'company_name': 'Acme SAS',
            'siren': '123456789',
            'role': 'Directeur',
            'status': 'Active',
            'beneficial_ownership_pct': 51.0,
            'financials': {},
        },
    ],
    'sanctions_pep': [],
    'offshore': [
        {
            'entity_name': 'Acme Holdings Ltd',
            'jurisdiction': 'British Virgin Islands',
            'role': 'Director',
            'dataset': 'Panama Papers',
        },
    ],
    'press_coverage': [
        {
            'title': 'Jean Dupont named CEO of Acme',
            'source': 'lemonde.fr',
            'date': '2025-01-15',
            'url': 'https://lemonde.fr/article',
            'sentiment': 'neutral',
        },
    ],
    'risk_assessment': {
        'level': 'MEDIUM',
        'factors': ['Offshore entity in BVI', 'No sanctions found'],
        'summary': 'Subject has offshore connections via Panama Papers but no sanctions or PEP listings.',
    },
    'sources_consulted': ['pappers', 'opensanctions', 'icij', 'gdelt', 'aleph'],
    'data_gaps': ['No Aleph records found'],
}


class TestPdfGeneration:
    def test_generate_pdf_returns_bytes(self):
        from app.report import generate_pdf
        pdf_bytes = generate_pdf(SAMPLE_BRIEF)
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes[:5] == b'%PDF-'

    def test_generate_pdf_contains_subject_name(self):
        from app.report import generate_pdf
        pdf_bytes = generate_pdf(SAMPLE_BRIEF)
        assert len(pdf_bytes) > 1000

    def test_generate_pdf_empty_sections(self):
        from app.report import generate_pdf
        minimal_brief = {
            'subject_name': 'Test Person',
            'generated_at': '2026-03-21T00:00:00Z',
            'identity': {'full_name': 'Test Person', 'aliases': [], 'birth_date': '', 'nationalities': [], 'addresses': []},
            'corporate_network': [],
            'sanctions_pep': [],
            'offshore': [],
            'press_coverage': [],
            'risk_assessment': {'level': 'LOW', 'factors': [], 'summary': 'No data found.'},
            'sources_consulted': [],
            'data_gaps': [],
        }
        pdf_bytes = generate_pdf(minimal_brief)
        assert pdf_bytes[:5] == b'%PDF-'


class TestSynthesis:
    @pytest.mark.asyncio
    async def test_fallback_without_api_key(self):
        from app.synthesis import synthesize_brief
        with patch('app.synthesis.ANTHROPIC_API_KEY', ''):
            brief = await synthesize_brief('Test Person', [])
        assert brief['subject_name'] == 'Test Person'
        assert brief['risk_assessment']['level'] == 'LOW'
        assert 'Claude synthesis unavailable' in brief['data_gaps']

    @pytest.mark.asyncio
    async def test_synthesis_calls_claude(self):
        from app.synthesis import synthesize_brief
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"identity": {"full_name": "Test"}, "corporate_network": [], "sanctions_pep": [], "offshore": [], "press_coverage": [], "risk_assessment": {"level": "LOW", "factors": [], "summary": "Clean."}, "sources_consulted": [], "data_gaps": []}')]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch('app.synthesis.ANTHROPIC_API_KEY', 'test-key'), \
             patch('app.synthesis.anthropic.Anthropic', return_value=mock_client):
            brief = await synthesize_brief('Test Person', [])

        assert brief['subject_name'] == 'Test Person'
        assert brief['generated_at'] is not None
        mock_client.messages.create.assert_called_once()


class TestConfirmEndpoint:
    def setup_method(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.db_fd)
        self.patcher = patch('app.db.DB_PATH', self.db_path)
        self.patcher.start()
        from app.db import init_db
        init_db()

    def teardown_method(self):
        self.patcher.stop()
        os.unlink(self.db_path)

    @pytest.mark.asyncio
    async def test_confirm_returns_generating(self):
        from app.db import create_scan, update_scan_complete
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        scan_id = create_scan('Jean Dupont', {})
        results = [SourceResult(
            source='pappers', query='Jean Dupont',
            matches=[SourceMatch(name='Jean Dupont', type='person', summary='Dir', url='http://ex.com')],
            duration_ms=100,
        )]
        update_scan_complete(scan_id, results, results, {}, ['pappers'], [], 100)

        with patch('app.main.run_report_generation', new_callable=AsyncMock):
            async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
                resp = await client.post(f'/api/v1/scan/{scan_id}/confirm')

            assert resp.status_code == 200
            assert resp.json()['status'] == 'generating'

    @pytest.mark.asyncio
    async def test_confirm_rejects_pending_scan(self):
        from app.db import create_scan
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        scan_id = create_scan('Test', {})

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            resp = await client.post(f'/api/v1/scan/{scan_id}/confirm')

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_report_download_not_ready(self):
        from app.db import create_scan
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        scan_id = create_scan('Test', {})

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            resp = await client.get(f'/api/v1/scans/{scan_id}/report')

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_report_download_when_ready(self):
        from app.db import create_scan, update_scan_complete, update_scan_report_ready
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        scan_id = create_scan('Jean Dupont', {})
        results = [SourceResult(source='test', query='Jean Dupont', matches=[], duration_ms=100)]
        update_scan_complete(scan_id, results, results, {}, [], [], 100)
        update_scan_report_ready(scan_id, {'subject': 'Jean Dupont'}, b'%PDF-fake')

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            resp = await client.get(f'/api/v1/scans/{scan_id}/report')

        assert resp.status_code == 200
        assert resp.headers['content-type'] == 'application/pdf'
        assert resp.content == b'%PDF-fake'

    @pytest.mark.asyncio
    async def test_brief_endpoint(self):
        from app.db import create_scan, update_scan_complete, update_scan_report_ready
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        scan_id = create_scan('Jean Dupont', {})
        results = [SourceResult(source='test', query='Jean Dupont', matches=[], duration_ms=100)]
        update_scan_complete(scan_id, results, results, {}, [], [], 100)
        brief = {'subject_name': 'Jean Dupont', 'level': 'LOW'}
        update_scan_report_ready(scan_id, brief, b'%PDF-fake')

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            resp = await client.get(f'/api/v1/scans/{scan_id}/brief')

        assert resp.status_code == 200
        assert resp.json()['subject_name'] == 'Jean Dupont'
