# Product Roadmap

## Phase 1: GitOps Infrastructure

**Goal:** Deploy a Docker-based FastAPI service on Hetzner VPS with GitOps workflow
**Success Criteria:** git push + manual workflow trigger deploys in under 90 seconds; API responds on HTTPS

### Features

- [x] Dockerfile for FastAPI service `S`
- [x] Setup VPS workflow (system deps, Docker, deploy user, nginx, certbot) `M`
- [x] Deploy workflow (docker build, restart, health check) `M`
- [x] Nginx reverse proxy with Let's Encrypt HTTPS `S`
- [x] Firewall hardening (UFW: 22, 80, 443 only) `XS`
- [ ] API key authentication middleware `XS`

### Dependencies

- Hetzner VPS provisioned with Ubuntu 24.04 LTS
- GitHub environment secrets configured

## Phase 2: Source Adapters

**Goal:** Build async adapters for all 5 data sources with normalised output
**Success Criteria:** Each adapter returns structured results or a clean timeout within 30 seconds

### Features

- [x] Base adapter interface (async, 30s timeout, normalised output) `S`
- [x] OCCRP Aleph adapter `M`
- [x] OpenSanctions adapter (POST /match/default) `M`
- [x] ICIJ OffshoreLeaks adapter (POST /reconcile) `S`
- [x] Pappers adapter (api_token query param) `S`
- [x] GDELT adapter (retry with backoff for 429) `S`
- [x] Parallel fan-out orchestrator (asyncio.gather) `S`
- [x] POST /api/v1/scan endpoint `S`
- [x] Ops web form (name, nationality, birth year, company, hints) `S`

### Dependencies

- Phase 1 complete
- API keys for OpenSanctions and Pappers (free tier)

## Phase 3: Claude Synthesis & Report Generation

**Goal:** Aggregate source results and produce AI-synthesised intelligence briefs as PDF and JSON
**Success Criteria:** POST /api/v1/scan returns a structured brief with risk score and downloadable PDF in under 90 seconds

### Features

- [ ] Claude synthesis prompt (aggregated JSON to structured UHNW brief) `M`
- [ ] Intelligence brief JSON schema (identity, entities, sanctions, offshore, press, risk score) `S`
- [ ] HTML report template `M`
- [ ] WeasyPrint PDF generation `S`
- [ ] PDF download from web form `S`

### Dependencies

- Phase 2 complete
- Claude API access (Anthropic API key)

## Phase 4: Aston Platform Integration (Future)

**Goal:** Connect Aston Rails app to OSINT pipeline
**Success Criteria:** New client creation in Aston triggers an automatic scan

### Features

- [ ] Aston calls POST /api/v1/scan on new client creation `M`
- [ ] Scan history: SQLite log of all scans with timestamps `S`
- [ ] JSON response stored and displayed in Aston UI `M`

### Dependencies

- Phase 3 complete
- Decision to integrate (DEC-TBD)

## Phase 5: Monitoring & Extended Sources (Future)

**Goal:** Add re-screening, alerting, and additional data sources
**Success Criteria:** Scheduled re-scans detect changes; alerts sent on HIGH/CRITICAL risk

### Features

- [ ] Scheduled re-screening against updated sanctions lists `L`
- [ ] Slack/email alert on HIGH or CRITICAL risk score `M`
- [ ] Companies House UK adapter `S`
- [ ] OpenCorporates adapter `M`
- [ ] RGPD compliance review and data retention policy `L`
- [ ] Audit logging for all scans `M`

### Dependencies

- Phase 4 complete (or standalone if integration deferred)
