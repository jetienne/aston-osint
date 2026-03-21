from app.models import SourceResult


def extract_facets(results: list[SourceResult]) -> dict:
    countries = set()
    birth_years = set()
    companies = {}

    for result in results:
        for match in result.matches:
            data = match.data
            properties = data.get('properties', {})

            for key in ('nationality', 'country', 'jurisdiction', 'country_codes'):
                val = properties.get(key) or data.get(key)
                if val:
                    if isinstance(val, list):
                        countries.update(v for v in val if v)
                    elif isinstance(val, str) and val:
                        countries.add(val)

            for key in ('birthDate', 'birth_year', 'date_naissance'):
                val = properties.get(key) or data.get(key)
                if val:
                    if isinstance(val, list):
                        for v in val:
                            year = _extract_year(v)
                            if year:
                                birth_years.add(year)
                    else:
                        year = _extract_year(val)
                        if year:
                            birth_years.add(year)

            for key in ('entreprises', 'companies'):
                items = data.get(key, [])
                for item in items:
                    name = item.get('nom_entreprise') or item.get('name')
                    if name and name not in companies:
                        siege = item.get('siege', {})
                        city = siege.get('ville', '')
                        country = siege.get('pays', '')
                        forme = item.get('forme_juridique', '')
                        activite = item.get('domaine_activite') or item.get('libelle_code_naf', '')

                        details = []
                        if city:
                            details.append(city)
                        if country and country != 'France':
                            details.append(country)
                        if forme:
                            details.append(forme)
                        if activite:
                            details.append(activite)

                        companies[name] = {
                            'value': name,
                            'label': name,
                            'detail': ' — '.join(details) if details else '',
                        }

    facets = []
    if len(countries) >= 2:
        facets.append({
            'field': 'country',
            'label': 'Country',
            'options': [{'value': c, 'label': c} for c in sorted(countries)],
        })
    if len(birth_years) >= 2:
        facets.append({
            'field': 'birth_year',
            'label': 'Birth year',
            'options': [{'value': y, 'label': y} for y in sorted(birth_years)],
        })
    if len(companies) >= 2:
        facets.append({
            'field': 'company',
            'label': 'Company',
            'options': sorted(companies.values(), key=lambda c: c['value']),
        })

    has_ambiguous = any(
        m.confidence in ('MEDIUM', 'LOW')
        for r in results
        for m in r.matches
    )

    return {
        'has_ambiguous': has_ambiguous,
        'facets': facets,
    }


def _extract_year(val) -> str | None:
    s = str(val).strip()
    if len(s) >= 4 and s[:4].isdigit():
        year = s[:4]
        if 1900 <= int(year) <= 2010:
            return year
    return None
