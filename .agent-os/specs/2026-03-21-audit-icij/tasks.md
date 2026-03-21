# Spec Tasks

## Tasks

- [ ] 1. Support additional entity types
  - [ ] 1.1 Write tests for Entity (companies) and Address searches
  - [ ] 1.2 Add Entity type query alongside Officer
  - [ ] 1.3 Use `company` kwarg to trigger Entity-type search
  - [ ] 1.4 Merge results from multiple type queries
  - [ ] 1.5 Verify all tests pass

- [ ] 2. Extract entity relationships
  - [ ] 2.1 Write tests for relationship extraction
  - [ ] 2.2 Fetch linked entities (officers → companies → intermediaries)
  - [ ] 2.3 Include relationship data in SourceMatch.data
  - [ ] 2.4 Verify all tests pass

- [ ] 3. Use batch reconciliation
  - [ ] 3.1 Write tests for multi-query batch requests
  - [ ] 3.2 Send person + company queries in single request
  - [ ] 3.3 Verify all tests pass

- [ ] 4. Add dataset filtering
  - [ ] 4.1 Write tests for dataset-specific search
  - [ ] 4.2 Allow filtering by dataset (Panama Papers, Paradise Papers, Pandora Papers)
  - [ ] 4.3 Include dataset source in SourceMatch summary
  - [ ] 4.4 Verify all tests pass

- [ ] 5. Improve result data extraction
  - [ ] 5.1 Write tests for richer node data parsing
  - [ ] 5.2 Extract country/jurisdiction from node data
  - [ ] 5.3 Extract dates (incorporation, inactivation) when available
  - [ ] 5.4 Verify all tests pass
