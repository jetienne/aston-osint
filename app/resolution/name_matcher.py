import re

from unidecode import unidecode


TITLE_PREFIXES = {
    'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'dame', 'lord', 'lady',
    'jr', 'sr', 'ii', 'iii', 'iv',
    'von', 'van', 'de', 'du', 'del', 'della', 'di', 'el', 'al', 'bin', 'ibn',
}


def normalise_name(name: str) -> set[str]:
    name = unidecode(name)
    name = name.lower()
    name = re.sub(r'[^a-z\s]', ' ', name)
    tokens = name.split()
    tokens = [t for t in tokens if t not in TITLE_PREFIXES and len(t) > 1]
    return set(tokens)


def is_name_match(query_name: str, result_name: str) -> bool:
    query_tokens = normalise_name(query_name)
    result_tokens = normalise_name(result_name)

    if not query_tokens or not result_tokens:
        return False

    if len(query_tokens) < 2:
        return query_tokens.issubset(result_tokens)

    return query_tokens.issubset(result_tokens)


def _match_any_name(query_name: str, match) -> bool:
    if is_name_match(query_name, match.name):
        return True

    alt_names = match.data.get('properties', {}).get('name', [])
    for alt in alt_names:
        if isinstance(alt, str) and is_name_match(query_name, alt):
            return True

    return False


def filter_results(query_name: str, results: list) -> list:
    from app.models import SourceResult

    filtered = []
    for result in results:
        if result.error is not None:
            filtered.append(result)
            continue

        kept_matches = [m for m in result.matches if _match_any_name(query_name, m)]
        filtered.append(SourceResult(
            source=result.source,
            query=result.query,
            matches=kept_matches,
            duration_ms=result.duration_ms,
            error=result.error,
        ))

    return filtered
