# Spec Tasks

## Tasks

- [ ] 1. Support non-Person schema types
  - [ ] 1.1 Write tests for Company and Organization schema search
  - [ ] 1.2 Use `company` kwarg to trigger Company schema query
  - [ ] 1.3 Handle mixed-schema results in response parsing
  - [ ] 1.4 Verify all tests pass

- [ ] 2. Add dataset filtering
  - [ ] 2.1 Write tests for dataset-specific matching
  - [ ] 2.2 Add option to search specific datasets (sanctions-only, PEP-only)
  - [ ] 2.3 Use `/match/{dataset}` endpoint when filtering requested
  - [ ] 2.4 Verify all tests pass

- [ ] 3. Use batch queries
  - [ ] 3.1 Write tests for multi-query requests
  - [ ] 3.2 Send person + company queries in single request (`q1`, `q2`)
  - [ ] 3.3 Merge results from multiple queries
  - [ ] 3.4 Verify all tests pass

- [ ] 4. Extract richer entity data
  - [ ] 4.1 Write tests for expanded field extraction
  - [ ] 4.2 Extract topics (PEP, sanctions, crime) from results
  - [ ] 4.3 Extract first_seen / last_seen temporal data
  - [ ] 4.4 Extract addresses and ID numbers when available
  - [ ] 4.5 Verify all tests pass

- [ ] 5. Add additional matching properties
  - [ ] 5.1 Write tests for address and ID-based matching
  - [ ] 5.2 Use `hints` kwarg to add extra matching context
  - [ ] 5.3 Add `properties.address` when location info available
  - [ ] 5.4 Verify all tests pass
