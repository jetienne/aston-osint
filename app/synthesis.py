import asyncio
import json
import logging
from datetime import datetime, timezone

import anthropic

from app.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

MAX_INPUT_CHARS = 100000

SYSTEM_PROMPT = """You are an intelligence analyst producing UHNW prospect briefs for a luxury brand's compliance and sales teams.

Given enriched data from multiple OSINT sources, produce a structured intelligence brief.
Be factual — cite which source each finding comes from. Flag uncertainties explicitly.
If data is missing or contradictory, note it in data_gaps.

Return valid JSON only, no markdown formatting."""

USER_PROMPT_TEMPLATE = """Subject: {subject_name}

Enriched data from OSINT sources:
{enriched_json}

Produce a JSON intelligence brief with this exact structure:
{{
  "identity": {{
    "full_name": "string",
    "aliases": ["string"],
    "birth_date": "string or empty",
    "nationalities": ["string"],
    "addresses": ["string"]
  }},
  "corporate_network": [
    {{
      "company_name": "string",
      "siren": "string or empty",
      "role": "string",
      "status": "string or empty",
      "beneficial_ownership_pct": null or number,
      "financials": {{}}
    }}
  ],
  "sanctions_pep": [
    {{
      "source": "string",
      "program": "string",
      "listed_since": "string or empty",
      "details": "string"
    }}
  ],
  "offshore": [
    {{
      "entity_name": "string",
      "jurisdiction": "string",
      "role": "string",
      "dataset": "string"
    }}
  ],
  "press_coverage": [
    {{
      "title": "string",
      "source": "string",
      "date": "string",
      "url": "string",
      "sentiment": "positive, negative, or neutral"
    }}
  ],
  "risk_assessment": {{
    "level": "LOW or MEDIUM or HIGH or CRITICAL",
    "factors": ["string"],
    "summary": "string"
  }},
  "sources_consulted": ["string"],
  "data_gaps": ["string"]
}}

Include only sections with actual data. Return empty arrays for sections with no findings.
The risk_assessment.summary should be 2-3 sentences explaining the overall risk profile.
Keep the response concise — limit press_coverage to the 10 most relevant articles.
Limit corporate_network to the 15 most significant companies."""


async def synthesize_brief(query: str, enriched_results: list) -> dict:
    if not ANTHROPIC_API_KEY:
        return _fallback_brief(query, enriched_results)

    enriched_data = _build_enriched_data(enriched_results)
    enriched_json = json.dumps(enriched_data, indent=2, default=str)

    if len(enriched_json) > MAX_INPUT_CHARS:
        logger.warning(f'Enriched data too large ({len(enriched_json)} chars), truncating')
        enriched_json = enriched_json[:MAX_INPUT_CHARS] + '\n... (truncated for token limit)'

    prompt = USER_PROMPT_TEMPLATE.format(
        subject_name=query,
        enriched_json=enriched_json,
    )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for attempt in range(3):
        try:
            response = client.messages.create(
                model='claude-sonnet-4-6',
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{'role': 'user', 'content': prompt}],
            )
            break
        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            logger.warning(f'Rate limited, waiting {wait}s (attempt {attempt + 1}/3)')
            await asyncio.sleep(wait)
    else:
        logger.error('Rate limited after 3 retries, using fallback brief')
        return _fallback_brief(query, enriched_results)

    response_text = response.content[0].text.strip()
    if response_text.startswith('```'):
        response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

    brief = json.loads(response_text)
    brief['subject_name'] = query
    brief['generated_at'] = datetime.now(timezone.utc).isoformat()
    return brief


def _build_enriched_data(enriched_results: list) -> list:
    enriched_data = []
    for result in enriched_results:
        if hasattr(result, 'source'):
            source_data = {
                'source': result.source,
                'matches': [_truncate_match(m) for m in result.matches[:5]],
            }
        else:
            source_data = result
        enriched_data.append(source_data)
    return enriched_data


def _truncate_match(m):
    data = dict(m.data)
    if 'enriched_articles' in data:
        data['enriched_articles'] = data['enriched_articles'][:10]
    if 'entreprises' in data:
        data['entreprises'] = data['entreprises'][:10]
    if 'beneficiaires_effectifs' in data:
        data['beneficiaires_effectifs'] = data['beneficiaires_effectifs'][:10]
    if 'finances' in data:
        data['finances'] = data['finances'][:3]
    if 'actes' in data:
        data['actes'] = data['actes'][:3]
    if 'bodacc' in data:
        data['bodacc'] = data['bodacc'][:3]
    if 'properties' in data and isinstance(data['properties'], dict):
        props = data['properties']
        for key in list(props.keys()):
            if isinstance(props[key], list) and len(props[key]) > 5:
                props[key] = props[key][:5]
    return {'name': m.name, 'type': m.type, 'summary': m.summary, 'data': data}


def _fallback_brief(query: str, enriched_results: list) -> dict:
    sources = []
    for result in enriched_results:
        if hasattr(result, 'source'):
            sources.append(result.source)

    return {
        'subject_name': query,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'identity': {'full_name': query, 'aliases': [], 'birth_date': '', 'nationalities': [], 'addresses': []},
        'corporate_network': [],
        'sanctions_pep': [],
        'offshore': [],
        'press_coverage': [],
        'risk_assessment': {
            'level': 'LOW',
            'factors': ['No Claude API key configured — unable to synthesize intelligence brief'],
            'summary': 'Automated synthesis unavailable. Raw data from sources is included below.',
        },
        'sources_consulted': sources,
        'data_gaps': ['Claude synthesis unavailable'],
    }
