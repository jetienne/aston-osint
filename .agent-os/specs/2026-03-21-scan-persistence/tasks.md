# Spec Tasks

## Tasks

- [ ] 1. SQLite database module
  - [ ] 1.1 Create `app/db.py` — init_db, save_scan, get_scan, list_scans, update_filtered_results
  - [ ] 1.2 Add Docker volume for /data in deploy.sh
  - [ ] 1.3 Call init_db on app startup
  - [ ] 1.4 Write tests for db module

- [ ] 2. Wire database into orchestrator
  - [ ] 2.1 Replace scan_store.save_scan with db.save_scan in orchestrator
  - [ ] 2.2 Save both raw_results and filtered_results after scan completes
  - [ ] 2.3 Update refine endpoint to read/write from database
  - [ ] 2.4 Remove scan_store.py

- [ ] 3. History API endpoints
  - [ ] 3.1 Add GET /api/v1/scans (list with pagination)
  - [ ] 3.2 Add GET /api/v1/scans/{scan_id} (full detail)
  - [ ] 3.3 Write tests for history endpoints

- [ ] 4. History UI
  - [ ] 4.1 Create history.html with scan list
  - [ ] 4.2 Add detail view (click scan to see results)
  - [ ] 4.3 Add "History" link to sidebar nav
  - [ ] 4.4 Add toggle to show raw vs filtered results in detail view

- [ ] 5. Deploy and test
  - [ ] 5.1 Deploy with Docker volume
  - [ ] 5.2 Run scans, verify they appear in history
  - [ ] 5.3 Restart container, verify scans persist
