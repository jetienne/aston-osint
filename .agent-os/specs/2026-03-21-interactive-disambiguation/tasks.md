# Spec Tasks

## Tasks

- [ ] 1. Scan state storage
  - [ ] 1.1 Create `app/scan_store.py` — in-memory store with UUID keys and 1-hour TTL
  - [ ] 1.2 Write tests for save, get, and expiry
  - [ ] 1.3 Update orchestrator to save raw results and return scan_id

- [ ] 2. Facet extraction
  - [ ] 2.1 Create `app/resolution/disambiguation.py` — extract facets (country, birth year, company, dataset) from match data
  - [ ] 2.2 Update POST /api/v1/scan response to include disambiguation facets
  - [ ] 2.3 Write tests for facet extraction

- [ ] 3. Refine endpoint
  - [ ] 3.1 Add POST /api/v1/scan/{scan_id}/refine endpoint
  - [ ] 3.2 Apply facet filters (OR within facet, AND across facets)
  - [ ] 3.3 Handle dismissed match indices
  - [ ] 3.4 Re-run Claude entity resolution on filtered set
  - [ ] 3.5 Write tests for refine endpoint

- [ ] 4. UI: match cards with accept/dismiss
  - [ ] 4.1 Redesign match display as cards with confidence badge
  - [ ] 4.2 Add dismiss button per match (tracks dismissed indices)
  - [ ] 4.3 Add accept button per match (sets confidence to HIGH locally)

- [ ] 5. UI: disambiguation facets
  - [ ] 5.1 Show multi-select pill groups above results for each facet
  - [ ] 5.2 Auto-submit on pill toggle (debounced 500ms) to refine endpoint
  - [ ] 5.3 Re-render results and facets on refine response

- [ ] 6. Deploy and test
  - [ ] 6.1 Deploy and test full flow: scan → facet filter → accept/dismiss
  - [ ] 6.2 Test with ambiguous name and verify multi-select filtering works
