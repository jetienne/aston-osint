from app.models import SourceMatch, SourceResult


def apply_facet_filters(results: list[SourceResult], filters: dict) -> list[SourceResult]:
    if not filters:
        return results

    filtered = []
    for result in results:
        if result.error is not None:
            filtered.append(result)
            continue

        kept = [m for m in result.matches if _match_passes_filters(m, filters)]
        filtered.append(SourceResult(
            source=result.source,
            query=result.query,
            matches=kept,
            duration_ms=result.duration_ms,
            error=result.error,
        ))

    return filtered


def apply_dismissed(results: list[SourceResult], dismissed: list[int]) -> list[SourceResult]:
    if not dismissed:
        return results

    dismissed_set = set(dismissed)
    flat_index = 0
    filtered = []

    for result in results:
        if result.error is not None:
            filtered.append(result)
            continue

        kept = []
        for match in result.matches:
            if flat_index not in dismissed_set:
                kept.append(match)
            flat_index += 1

        filtered.append(SourceResult(
            source=result.source,
            query=result.query,
            matches=kept,
            duration_ms=result.duration_ms,
            error=result.error,
        ))

    return filtered


def _match_passes_filters(match: SourceMatch, filters: dict) -> bool:
    for field, selected_values in filters.items():
        if not selected_values:
            continue
        match_values = _extract_field_values(match, field)
        if not match_values:
            continue
        if not match_values.intersection(set(selected_values)):
            return False
    return True


def _extract_field_values(match: SourceMatch, field: str) -> set:
    data = match.data
    properties = data.get('properties', {})
    values = set()

    if field == 'country':
        for key in ('nationality', 'country', 'jurisdiction', 'country_codes'):
            val = properties.get(key) or data.get(key)
            if val:
                if isinstance(val, list):
                    values.update(v for v in val if v)
                elif isinstance(val, str) and val:
                    values.add(val)

    elif field == 'birth_year':
        for key in ('birthDate', 'birth_year', 'date_naissance'):
            val = properties.get(key) or data.get(key)
            if val:
                items = val if isinstance(val, list) else [val]
                for v in items:
                    s = str(v).strip()
                    if len(s) >= 4 and s[:4].isdigit():
                        values.add(s[:4])

    elif field == 'company':
        for key in ('entreprises', 'companies'):
            for item in data.get(key, []):
                name = item.get('nom_entreprise') or item.get('name')
                if name:
                    values.add(name)

    elif field == 'dataset':
        for ds in data.get('datasets', []):
            if ds:
                values.add(ds)

    return values
