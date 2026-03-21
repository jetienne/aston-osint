# Spec Tasks

## Tasks

- [x] 1. Scan state storage
  - [x] 1.1 Create `app/scan_store.py` — in-memory store with UUID keys and 1-hour TTL
  - [x] 1.2 Write tests for save, get, and expiry
  - [x] 1.3 Update orchestrator to save raw results and return scan_id

- [x] 2. Facet extraction
  - [x] 2.1 Create `app/resolution/disambiguation.py` — extract facets (country, birth year, company, dataset) from match data
  - [x] 2.2 Update POST /api/v1/scan response to include disambiguation facets
  - [x] 2.3 Write tests for facet extraction (20 tests)

- [x] 3. Refine endpoint
  - [x] 3.1 Add POST /api/v1/scan/{scan_id}/refine endpoint
  - [x] 3.2 Apply facet filters (OR within facet, AND across facets)
  - [x] 3.3 Handle dismissed match indices
  - [x] 3.4 Re-run Claude entity resolution on filtered set
  - [x] 3.5 Write tests for facet filter and dismiss (15 tests)

- [x] 4. UI: wizard flow + match cards
  - [x] 4.1 Simplified search form (name only)
  - [x] 4.2 Wizard: one facet question at a time with multi-select pills
  - [x] 4.3 Skip button per question, Next/Show results to advance
  - [x] 4.4 Match cards with source tag, confidence badge, dismiss button
  - [x] 4.5 Refine call after wizard completes with selected filters

- [ ] 6. Deploy and test
  - [ ] 6.1 Deploy and test full flow: scan → facet filter → accept/dismiss
  - [ ] 6.2 Test with ambiguous name and verify multi-select filtering works
