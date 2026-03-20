# Spec Tasks

## Tasks

- [x] 1. Create base adapter interface and models
  - [x] 1.1 Create `app/models.py` with SourceMatch and SourceResult dataclasses
  - [x] 1.2 Create `app/adapters/base.py` with BaseAdapter ABC
  - [x] 1.3 Create `app/config.py` with settings (API keys from env vars)
  - [x] 1.4 Add httpx to requirements.txt

- [x] 2. Implement source adapters
  - [x] 2.1 Create `app/adapters/aleph.py` — OCCRP Aleph adapter
  - [x] 2.2 Create `app/adapters/opensanctions.py` — OpenSanctions adapter
  - [x] 2.3 Create `app/adapters/icij.py` — ICIJ OffshoreLeaks adapter
  - [x] 2.4 Create `app/adapters/pappers.py` — Pappers adapter
  - [x] 2.5 Create `app/adapters/gdelt.py` — GDELT adapter

- [x] 3. Implement orchestrator and wire API
  - [x] 3.1 Create `app/orchestrator.py` — parallel fan-out with asyncio.gather
  - [x] 3.2 Add POST /api/v1/scan endpoint to main.py (returns raw source results)
  - [x] 3.3 Update GET /api/v1/status to list adapters and availability
  - [x] 3.4 Update Dockerfile and requirements.txt

- [ ] 4. Test and deploy
  - [ ] 4.1 Deploy and verify POST /api/v1/scan returns results
  - [ ] 4.2 Add OPENSANCTIONS_API_KEY and PAPPERS_API_KEY to .env on server
  - [ ] 4.3 Test with known names (e.g. "Viktor Vekselberg")
