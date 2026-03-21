import json

import anthropic

from app.config import ANTHROPIC_API_KEY
from app.models import SourceResult

SYSTEM_PROMPT = """You are an entity resolution system. You determine whether search results refer to the same person as the query.

For each candidate, consider:
- Name similarity (transliterations, abbreviations, middle names, maiden names)
- Birth year (if available in both query and candidate data)
- Nationality (if available)
- Company affiliations (if available)
- Any other contextual signals in the candidate data

Return valid JSON only, no markdown formatting."""

USER_PROMPT_TEMPLATE = """Query person:
- Name: {name}
{context_lines}

Candidates from OSINT sources:
{candidates_json}

For each candidate, decide whether it refers to the same person as the query.

Return JSON in this exact format:
{{
  "resolutions": [
    {{
      "index": 0,
      "decision": "keep" or "drop",
      "confidence": "HIGH" or "MEDIUM" or "LOW",
      "rationale": "one sentence explaining your decision"
    }}
  ]
}}"""


async def resolve_entities(query: str, results: list[SourceResult], **kwargs) -> list[SourceResult]:
    if not ANTHROPIC_API_KEY:
        return results

    candidates = []
    candidate_map = []

    for source_idx, result in enumerate(results):
        for match_idx, match in enumerate(result.matches):
            candidates.append({
                'index': len(candidates),
                'source': result.source,
                'name': match.name,
                'type': match.type,
                'summary': match.summary,
                'data': match.data,
            })
            candidate_map.append((source_idx, match_idx))

    if not candidates:
        return results

    context_lines = ''
    if kwargs.get('birth_year'):
        context_lines += f'- Birth year: {kwargs["birth_year"]}\n'
    if kwargs.get('nationality'):
        context_lines += f'- Nationality: {kwargs["nationality"]}\n'
    if kwargs.get('company'):
        context_lines += f'- Company: {kwargs["company"]}\n'

    prompt = USER_PROMPT_TEMPLATE.format(
        name=query,
        context_lines=context_lines.strip() or '- No additional context',
        candidates_json=json.dumps(candidates, indent=2, default=str),
    )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{'role': 'user', 'content': prompt}],
    )

    response_text = response.content[0].text.strip()
    if response_text.startswith('```'):
        response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

    parsed = json.loads(response_text)
    resolutions = {r['index']: r for r in parsed.get('resolutions', [])}

    for candidate_idx, (source_idx, match_idx) in enumerate(candidate_map):
        resolution = resolutions.get(candidate_idx)
        if resolution:
            match = results[source_idx].matches[match_idx]
            match.confidence = resolution.get('confidence')
            match.rationale = resolution.get('rationale')

    drop_indices = set()
    for r in parsed.get('resolutions', []):
        if r.get('decision') == 'drop':
            drop_indices.add(r['index'])

    filtered = []
    for source_idx, result in enumerate(results):
        kept = []
        for match_idx, match in enumerate(result.matches):
            candidate_idx = next(
                (ci for ci, (si, mi) in enumerate(candidate_map) if si == source_idx and mi == match_idx),
                None,
            )
            if candidate_idx not in drop_indices:
                kept.append(match)
        filtered.append(SourceResult(
            source=result.source,
            query=result.query,
            matches=kept,
            duration_ms=result.duration_ms,
            error=result.error,
        ))

    return filtered
