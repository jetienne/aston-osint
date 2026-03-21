# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-21-audit-pappers/spec.md

## Adapter Identity

| Aspect | Detail |
|---|---|
| **File** | `app/adapters/pappers.py` |
| **Class** | `PappersAdapter` extends `BaseAdapter` |
| **Adapter name** | `pappers` |
| **Base URL** | `https://api.pappers.fr/v2` |
| **Endpoint** | `GET /recherche-dirigeants` |
| **Auth** | Required `api_token` query parameter |
| **Env var** | `PAPPERS_API_KEY` |
| **Timeout** | 30s (inherited from BaseAdapter) |

## Query Construction

| Parameter | Value | Notes |
|---|---|---|
| `q` | `<query>` | Search term, not quoted |
| `par_page` | `10` | Hardcoded result limit |
| `api_token` | env var value | Required, returns error if missing |

Early return with `SourceResult(error='PAPPERS_API_KEY not configured')` if key is not set.

## Response Parsing

Reads from `data['resultats']`. For each dirigeant:

| Extracted Field | Source Path | Mapped To |
|---|---|---|
| name | `"{prenom} {nom}"` | `SourceMatch.name` |
| type | hardcoded `'person'` | `SourceMatch.type` |
| summary | `"{qualite} — {company_names}"` | `SourceMatch.summary` |
| url | `https://www.pappers.fr/entreprise/{siren}` | `SourceMatch.url` (first company's SIREN) |

### Entreprises Sub-extraction (first 5 companies per dirigeant)

| Field | Source Path |
|---|---|
| nom_entreprise | `entreprises[].nom_entreprise` |
| siren | `entreprises[].siren` |
| forme_juridique | `entreprises[].forme_juridique` |
| domaine_activite | `entreprises[].domaine_activite` |
| libelle_code_naf | `entreprises[].libelle_code_naf` |
| siege | `entreprises[].siege` (full dict) |

Summary uses first 3 company names; data stores first 5 companies.

## kwargs Usage

None. All kwargs (`nationality`, `birth_year`, `company`, `hints`) are ignored.

## Error Handling

- Explicit check: returns error if `PAPPERS_API_KEY` is not configured
- Inherited from BaseAdapter: any exception caught and returned as error
- API token is redacted in error messages by BaseAdapter's regex

## Known Limitations

- Only searches executives (`recherche-dirigeants`) — does not search companies directly
- France-only geographic coverage
- Hard limit of 10 results per page, no pagination
- Does not extract date of birth from dirigeant record
- Does not extract address details from dirigeant record
- `company` kwarg could refine search via `/recherche` endpoint but is ignored
- URL always points to first company — if dirigeant has no companies, URL is empty string
- Only stores first 5 entreprises per dirigeant (summarises first 3)

## Notable Pappers API Capabilities Not Used

- `GET /recherche` — search companies directly by name
- `GET /entreprise?siren=...` — full company details (financials, legal publications, etc.)
- `GET /entreprise?siren=...&extrait_rcs=true` — RCS extract
- Beneficial ownership data (`beneficiaires_effectifs`)
- Financial data (chiffre d'affaires, resultat, etc.)
- Legal publications (actes, annonces BODACC)
- Dirigeant birth date (`date_naissance`, `date_naissance_formatee`)
- Pagination (`page` parameter for multi-page results)
- Company status and legal proceedings
