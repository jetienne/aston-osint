# Spec Tasks

## Tasks

- [ ] 1. Add company search endpoint
  - [ ] 1.1 Write tests for company search via /recherche
  - [ ] 1.2 Use `company` kwarg to trigger GET /recherche
  - [ ] 1.3 Merge dirigeant and company results
  - [ ] 1.4 Verify all tests pass

- [ ] 2. Extract richer dirigeant data
  - [ ] 2.1 Write tests for expanded dirigeant fields
  - [ ] 2.2 Extract date_naissance / date_naissance_formatee
  - [ ] 2.3 Extract address details from dirigeant record
  - [ ] 2.4 Verify all tests pass

- [ ] 3. Fetch company details
  - [ ] 3.1 Write tests for company detail enrichment
  - [ ] 3.2 Call GET /entreprise?siren=... for top company matches
  - [ ] 3.3 Extract beneficial ownership (beneficiaires_effectifs)
  - [ ] 3.4 Extract financial data (chiffre_affaires, resultat)
  - [ ] 3.5 Verify all tests pass

- [ ] 4. Add pagination
  - [ ] 4.1 Write tests for multi-page results
  - [ ] 4.2 Add `page` parameter support
  - [ ] 4.3 Aggregate results across pages up to a configurable limit
  - [ ] 4.4 Verify all tests pass

- [ ] 5. Extract legal publications
  - [ ] 5.1 Write tests for legal publication extraction
  - [ ] 5.2 Fetch actes and annonces BODACC for matched companies
  - [ ] 5.3 Include legal events in SourceMatch.data
  - [ ] 5.4 Verify all tests pass
