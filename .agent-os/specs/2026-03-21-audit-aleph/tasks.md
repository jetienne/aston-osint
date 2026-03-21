# Spec Tasks

## Tasks

- [ ] 1. Add entity type filtering
  - [ ] 1.1 Write tests for schema-based filtering (Person, Company, LegalEntity)
  - [ ] 1.2 Add `filter:schemata` parameter to query
  - [ ] 1.3 Use `company` kwarg to search Company schema when provided
  - [ ] 1.4 Verify all tests pass

- [ ] 2. Add country/jurisdiction filtering
  - [ ] 2.1 Write tests for country filtering
  - [ ] 2.2 Use `nationality` kwarg to add `filter:countries` parameter
  - [ ] 2.3 Verify all tests pass

- [ ] 3. Increase result coverage
  - [ ] 3.1 Write tests for pagination
  - [ ] 3.2 Add pagination via `offset` parameter
  - [ ] 3.3 Increase or make `limit` configurable
  - [ ] 3.4 Verify all tests pass

- [ ] 4. Extract richer entity data
  - [ ] 4.1 Write tests for expanded field extraction
  - [ ] 4.2 Extract countries, addresses, dates from `properties`
  - [ ] 4.3 Extract linked entities / relationships
  - [ ] 4.4 Verify all tests pass

- [ ] 5. Improve query flexibility
  - [ ] 5.1 Write tests for unquoted / fuzzy search option
  - [ ] 5.2 Add option for non-quoted query (fuzzy match)
  - [ ] 5.3 Use `hints` kwarg to append context to query
  - [ ] 5.4 Verify all tests pass
