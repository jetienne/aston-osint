# Spec Tasks

## Tasks

- [ ] 1. SQLite database module
  - [ ] 1.1 Create `app/db.py` — init_db, create_scan, update_scan_running/complete/failed, get_scan, list_scans, update_filtered_results
  - [ ] 1.2 Add Docker volume (`-v aston-osint-data:/data`) in deploy.sh
  - [ ] 1.3 Call init_db on FastAPI startup
  - [ ] 1.4 Write tests for db module

- [ ] 2. Async scan execution
  - [ ] 2.1 Update POST /api/v1/scan to return immediately with scan_id + status
  - [ ] 2.2 Move scan logic to background task (asyncio.create_task)
  - [ ] 2.3 Background task updates status in db (running → complete/failed)
  - [ ] 2.4 Remove scan_store.py, update refine endpoint to use db

- [ ] 3. Polling and history API
  - [ ] 3.1 Add GET /api/v1/scans/{id} (status + results when complete)
  - [ ] 3.2 Add GET /api/v1/scans (list with pagination)
  - [ ] 3.3 Write tests for API endpoints

- [ ] 4. Update scan UI for polling
  - [ ] 4.1 POST /scan returns immediately, start polling every 2s
  - [ ] 4.2 Show loading cards while polling
  - [ ] 4.3 On complete: show wizard or results
  - [ ] 4.4 On failed: show error

- [ ] 5. History UI
  - [ ] 5.1 Create history.html with scan list (cards with status badge)
  - [ ] 5.2 Add detail view (click scan → full results)
  - [ ] 5.3 Add "History" link to sidebar nav on all pages
  - [ ] 5.4 Add toggle for raw vs filtered results in detail view

- [ ] 6. Deploy and test
  - [ ] 6.1 Deploy with Docker volume
  - [ ] 6.2 Verify scans persist across container restarts
  - [ ] 6.3 Verify polling works end-to-end
