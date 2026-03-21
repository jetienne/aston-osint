# Spec Tasks

## Tasks

- [x] 1. Add company search endpoint
  - [x] 1.1 Write tests for company search via /recherche
  - [x] 1.2 Use `company` kwarg to trigger GET /recherche
  - [x] 1.3 Merge dirigeant and company results
  - [x] 1.4 Verify all tests pass

- [x] 2. Extract richer dirigeant data
  - [x] 2.1 Write tests for expanded dirigeant fields
  - [x] 2.2 Extract date_naissance / date_naissance_formatee
  - [x] 2.3 Extract address details from dirigeant record
  - [x] 2.4 Verify all tests pass

- [x] 3. Fetch company details
  - [x] 3.1 Write tests for company detail enrichment
  - [x] 3.2 Call GET /entreprise?siren=... for top company matches
  - [x] 3.3 Extract beneficial ownership (beneficiaires_effectifs)
  - [x] 3.4 Extract financial data (chiffre_affaires, resultat)
  - [x] 3.5 Verify all tests pass

- [x] 4. Add pagination
  - [x] 4.1 Write tests for multi-page results
  - [x] 4.2 Add `page` parameter support
  - [x] 4.3 Aggregate results across pages up to a configurable limit
  - [x] 4.4 Verify all tests pass

- [x] 5. Extract legal publications
  - [x] 5.1 Write tests for legal publication extraction
  - [x] 5.2 Fetch actes and annonces BODACC for matched companies
  - [x] 5.3 Include legal events in SourceMatch.data
  - [x] 5.4 Verify all tests pass
