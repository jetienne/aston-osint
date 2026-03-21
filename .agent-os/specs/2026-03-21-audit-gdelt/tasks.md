# Spec Tasks

## Tasks

- [ ] 1. Expand time window and result count
  - [ ] 1.1 Write tests for configurable timespan and maxrecords
  - [ ] 1.2 Make `timespan` configurable (default 12months or longer)
  - [ ] 1.3 Increase `maxrecords` (up to 250)
  - [ ] 1.4 Verify all tests pass

- [ ] 2. Add language and country filtering
  - [ ] 2.1 Write tests for sourcelang and sourcecountry filters
  - [ ] 2.2 Add `sourcelang` parameter based on nationality/context
  - [ ] 2.3 Add `sourcecountry` parameter when relevant
  - [ ] 2.4 Verify all tests pass

- [ ] 3. Parse tone data
  - [ ] 3.1 Write tests for tone field parsing
  - [ ] 3.2 Parse semicolon-separated tone string into structured scores (overall, positive, negative, polarity, activity)
  - [ ] 3.3 Include parsed tone in SourceMatch.data
  - [ ] 3.4 Verify all tests pass

- [ ] 4. Use GKG mode for entity extraction
  - [ ] 4.1 Write tests for GKG query and response parsing
  - [ ] 4.2 Add a second query using GKG mode to extract persons, orgs, themes, locations
  - [ ] 4.3 Merge GKG entity data with article results
  - [ ] 4.4 Verify all tests pass

- [ ] 5. Improve query construction
  - [ ] 5.1 Write tests for enhanced query building
  - [ ] 5.2 Use `company` kwarg to add co-occurrence terms (NEAR operator)
  - [ ] 5.3 Use `hints` kwarg to append context to query
  - [ ] 5.4 Remove hardcoded 2s initial sleep (use backoff only on 429)
  - [ ] 5.5 Verify all tests pass
