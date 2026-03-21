from unittest.mock import MagicMock, patch

from app.models import SourceMatch, SourceResult
from app.resolution.claude_resolver import resolve_entities

import pytest


def _make_match(name, type='person', summary='', url='', data=None):
    return SourceMatch(name=name, type=type, summary=summary, url=url, data=data or {})


def _make_result(source, matches):
    return SourceResult(
        source=source,
        query='test',
        matches=matches,
        duration_ms=100,
    )


def _mock_claude_response(resolutions):
    import json
    response = MagicMock()
    response.content = [MagicMock(text=json.dumps({'resolutions': resolutions}))]
    return response


class TestResolveEntitiesNoKey:
    @pytest.mark.asyncio
    async def test_returns_unchanged_without_api_key(self):
        results = [_make_result('test', [_make_match('Irina Dunaeva')])]
        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', ''):
            resolved = await resolve_entities('Irina Dunaeva', results)
        assert len(resolved[0].matches) == 1
        assert resolved[0].matches[0].name == 'Irina Dunaeva'


class TestResolveEntitiesNoMatches:
    @pytest.mark.asyncio
    async def test_returns_unchanged_with_no_matches(self):
        results = [_make_result('test', [])]
        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'):
            resolved = await resolve_entities('Irina Dunaeva', results)
        assert len(resolved[0].matches) == 0


class TestResolveEntitiesWithClaude:
    @pytest.mark.asyncio
    async def test_drops_rejected_matches(self):
        results = [
            _make_result('opensanctions', [
                _make_match('Irina Dunaeva'),
                _make_match('Irina Dunaeva-Smith'),
            ]),
        ]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'keep', 'confidence': 'HIGH', 'rationale': 'Exact match'},
            {'index': 1, 'decision': 'drop', 'confidence': 'LOW', 'rationale': 'Different person'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert len(resolved[0].matches) == 1
        assert resolved[0].matches[0].name == 'Irina Dunaeva'

    @pytest.mark.asyncio
    async def test_sets_confidence_and_rationale(self):
        results = [
            _make_result('icij', [_make_match('Irina Dunaeva')]),
        ]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'keep', 'confidence': 'MEDIUM', 'rationale': 'Name matches but no birth year to confirm'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert resolved[0].matches[0].confidence == 'MEDIUM'
        assert resolved[0].matches[0].rationale == 'Name matches but no birth year to confirm'

    @pytest.mark.asyncio
    async def test_multiple_sources(self):
        results = [
            _make_result('aleph', [_make_match('Irina Dunaeva')]),
            _make_result('icij', [_make_match('Dunaeva Irina V.')]),
            _make_result('opensanctions', [_make_match('Irina Dunaeva')]),
        ]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'keep', 'confidence': 'HIGH', 'rationale': 'Exact match'},
            {'index': 1, 'decision': 'keep', 'confidence': 'MEDIUM', 'rationale': 'Likely same person with middle initial'},
            {'index': 2, 'decision': 'keep', 'confidence': 'HIGH', 'rationale': 'Exact match'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert len(resolved[0].matches) == 1
        assert len(resolved[1].matches) == 1
        assert len(resolved[2].matches) == 1

    @pytest.mark.asyncio
    async def test_preserves_error_results(self):
        results = [
            SourceResult(source='pappers', query='test', error='timeout'),
            _make_result('aleph', [_make_match('Irina Dunaeva')]),
        ]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'keep', 'confidence': 'HIGH', 'rationale': 'Match'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert resolved[0].error == 'timeout'
        assert len(resolved[0].matches) == 0
        assert len(resolved[1].matches) == 1

    @pytest.mark.asyncio
    async def test_passes_context_to_prompt(self):
        results = [_make_result('test', [_make_match('Irina Dunaeva')])]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'keep', 'confidence': 'HIGH', 'rationale': 'Match'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            await resolve_entities(
                'Irina Dunaeva', results,
                birth_year=1975, nationality='Russia', company='Renova',
            )

            call_args = mock_client.messages.create.call_args
            prompt = call_args.kwargs['messages'][0]['content']
            assert 'Birth year: 1975' in prompt
            assert 'Nationality: Russia' in prompt
            assert 'Company: Renova' in prompt

    @pytest.mark.asyncio
    async def test_handles_markdown_wrapped_response(self):
        results = [_make_result('test', [_make_match('Irina Dunaeva')])]

        response = MagicMock()
        response.content = [MagicMock(
            text='```json\n{"resolutions": [{"index": 0, "decision": "keep", "confidence": "HIGH", "rationale": "Match"}]}\n```'
        )]

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert len(resolved[0].matches) == 1
        assert resolved[0].matches[0].confidence == 'HIGH'

    @pytest.mark.asyncio
    async def test_drops_all_when_all_rejected(self):
        results = [
            _make_result('test', [
                _make_match('Irina Petrova'),
                _make_match('Irina Sidorova'),
            ]),
        ]
        mock_response = _mock_claude_response([
            {'index': 0, 'decision': 'drop', 'confidence': 'HIGH', 'rationale': 'Different surname'},
            {'index': 1, 'decision': 'drop', 'confidence': 'HIGH', 'rationale': 'Different surname'},
        ])

        with patch('app.resolution.claude_resolver.ANTHROPIC_API_KEY', 'fake-key'), \
             patch('app.resolution.claude_resolver.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.Anthropic.return_value = mock_client

            resolved = await resolve_entities('Irina Dunaeva', results)

        assert len(resolved[0].matches) == 0
