# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-entity-resolution/spec.md

## Technical Requirements

### Architecture: Two-Pass Filtering

```
Raw source results (all 5 adapters)
        │
        ▼
  Pass 1: Local Name Matcher (fast, no API call)
  - Normalise query name and result names
  - Require both first name AND last name tokens to appear
  - Drop obvious non-matches
        │
        ▼
  Pass 2: Claude Entity Resolution (for remaining matches)
  - Send query context + candidate matches to Claude
  - Claude returns: keep/drop + confidence + rationale
        │
        ▼
  Filtered results with confidence levels
```

### Pass 1: Local Name Matcher

#### Name Normalisation

```python
def normalise_name(name: str) -> set[str]:
    """Convert a name to a set of normalised tokens for comparison."""
    # 1. Lowercase
    # 2. Remove diacritics (é→e, ü→u, etc.)
    # 3. Transliterate Cyrillic to Latin (unidecode)
    # 4. Remove punctuation (hyphens, dots, commas)
    # 5. Split into tokens
    # 6. Remove common prefixes/suffixes (Mr, Mrs, Dr, Jr, Sr, von, de, van)
    return set of normalised tokens
```

#### Matching Rule

```python
def is_name_match(query_name: str, result_name: str) -> bool:
    query_tokens = normalise_name(query_name)
    result_tokens = normalise_name(result_name)

    if len(query_tokens) < 2:
        # Single-word query: require exact token match
        return query_tokens.issubset(result_tokens)

    # Multi-word query: require ALL query tokens to appear in result
    # This ensures both first AND last name match
    return query_tokens.issubset(result_tokens)
```

This means:
- "Irina Dunaeva" → tokens: {"irina", "dunaeva"}
- "Oxana Dunaeva" → tokens: {"oxana", "dunaeva"} → MISS (no "irina")
- "Dunaeva Irina" → tokens: {"dunaeva", "irina"} → MATCH (order doesn't matter)
- "Irina Liner" → tokens: {"irina", "liner"} → MISS (no "dunaeva")

#### Edge Cases

- "Jean-Pierre Dupont" → tokens: {"jean", "pierre", "dupont"} — matches "Dupont Jean Pierre"
- Cyrillic "Ирина Дунаева" → transliterated to {"irina", "dunaeva"} — matches Latin variant

### Pass 2: Claude Entity Resolution

For matches that pass the local filter, Claude receives:

```json
{
  "query": {
    "name": "Irina Dunaeva",
    "birth_year": 1975,
    "nationality": "Russia",
    "company": "Renova Group"
  },
  "candidates": [
    {
      "source": "opensanctions",
      "name": "Irina Dunaeva",
      "summary": "Person — datasets: wd_peps (score: 0.95)",
      "data": { ... }
    },
    {
      "source": "icij",
      "name": "Dunaeva, Irina Vladimirovna",
      "summary": "Score: 85.2 — Officer",
      "data": { ... }
    }
  ]
}
```

Claude prompt:

```
You are an entity resolution system. For each candidate, determine whether
it refers to the same person as the query.

Consider:
- Name similarity (transliterations, abbreviations, middle names)
- Birth year (if available in both query and candidate)
- Nationality (if available)
- Company affiliations (if available)
- Any other contextual signals in the candidate data

For each candidate, return:
- decision: "keep" or "drop"
- confidence: "HIGH", "MEDIUM", or "LOW"
- rationale: one sentence explaining your decision
```

Claude response:

```json
{
  "resolutions": [
    {
      "index": 0,
      "decision": "keep",
      "confidence": "HIGH",
      "rationale": "Exact name match, Russian nationality consistent with PEP dataset"
    },
    {
      "index": 1,
      "decision": "keep",
      "confidence": "MEDIUM",
      "rationale": "Name matches with patronymic added; cannot confirm identity without birth year"
    }
  ]
}
```

### Updated SourceMatch Model

```python
@dataclass
class SourceMatch:
    name: str
    type: str
    summary: str
    url: str
    data: dict = field(default_factory=dict)
    confidence: str | None = None    # HIGH, MEDIUM, LOW
    rationale: str | None = None     # Claude's explanation
```

### Integration with Orchestrator

```python
async def run_scan(query: str, **kwargs) -> dict:
    # 1. Fan out to all sources
    raw_results = await asyncio.gather(...)

    # 2. Pass 1: local name filtering
    filtered = local_name_filter(query, raw_results)

    # 3. Pass 2: Claude entity resolution (if matches remain)
    if has_matches(filtered):
        resolved = await claude_resolve(query, filtered, **kwargs)
    else:
        resolved = filtered

    # 4. Return resolved results
    return format_response(resolved)
```

### File Structure

```
app/
├── resolution/
│   ├── __init__.py
│   ├── name_matcher.py    # normalise_name, is_name_match
│   └── claude_resolver.py # Claude entity resolution
├── ...
```

### Configuration

- `ANTHROPIC_API_KEY` — already in config.py, needed for Claude calls
- Claude model: use `claude-sonnet-4-6` for speed (entity resolution doesn't need opus)

## External Dependencies

- **unidecode** — Transliterate Unicode to ASCII (Cyrillic→Latin, diacritics removal)
- **Justification:** Standard library for name transliteration, lightweight, no API calls
- **anthropic** — Anthropic Python SDK for Claude API calls
- **Justification:** Required for Pass 2 entity resolution
