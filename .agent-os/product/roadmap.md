# Product Roadmap

## Phase 1: GitOps Infrastructure

**Goal:** Deploy a Docker-based FastAPI service on Hetzner VPS with GitOps workflow
**Success Criteria:** git push + manual workflow trigger deploys in under 90 seconds; API responds on HTTPS with API key auth

### Features

- [ ] Dockerfile for FastAPI service `S`
- [ ] Setup VPS workflow (system deps, Docker, deploy user, nginx, certbot) `M`
- [ ] Deploy workflow (docker build, restart, health check) `M`
- [ ] Nginx reverse proxy with Let's Encrypt HTTPS `S`
- [ ] API key authentication middleware `XS`
- [ ] Firewall hardening (UFW: 22, 80, 443 only) `XS`

### Dependencies

- Hetzner VPS provisioned with Ubuntu 24.04 LTS
- GitHub environment secrets configured

## Phase 2: Source Adapters

**Goal:** Build async adapters for all 5 data sources with normalised output
**Success Criteria:** Each adapter returns structured results or a clean timeout within 30 seconds

### Features

- [ ] Base adapter interface (async, 30s timeout, normalised output) `S`
- [ ] OCCRP Aleph adapter `M`
- [ ] OpenSanctions adapter `M`
- [ ] ICIJ OffshoreLeaks adapter `S`
- [ ] Pappers adapter `S`
- [ ] GDELT adapter `S`
- [ ] Parallel fan-out orchestrator (asyncio.gather) `S`

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
- [ ] POST /api/v1/scan endpoint (full pipeline: sources → Claude → PDF) `M`

### Dependencies

- Phase 2 complete
- Claude API access (Anthropic API key)

## Phase 4: Ops Web Form

**Goal:** Provide a simple web interface for non-technical ops staff to run scans
**Success Criteria:** Ops user enters a name in a browser form, receives a PDF download

### Features

- [ ] Single-page HTML form (name, nationality, company, hints, output format) `S`
- [ ] Form submission to POST /api/v1/scan `XS`
- [ ] Inline PDF display or download trigger `S`
- [ ] Loading state and error handling `XS`
- [ ] Served by nginx at root path (no build step) `XS`

### Dependencies

- Phase 3 complete

## Phase 5: Aston Platform Integration (Future)

**Goal:** Connect Aston Rails app to OSINT pipeline
**Success Criteria:** New client creation in Aston triggers an automatic scan

### Features

- [ ] Aston calls POST /api/v1/scan on new client creation `M`
- [ ] Scan history: SQLite log of all scans with timestamps `S`
- [ ] JSON response stored and displayed in Aston UI `M`

### Dependencies

- Phase 4 complete
- Decision to integrate (DEC-TBD)

## Phase 6: Monitoring & Extended Sources (Future)

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

- Phase 5 complete (or standalone if integration deferred)
