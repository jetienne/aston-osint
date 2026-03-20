# Product Roadmap

## Phase 1: GitOps Infrastructure

**Goal:** Deploy SpiderFoot on Hetzner VPS with fully automated GitOps workflow
**Success Criteria:** git push to main deploys in under 60 seconds; SpiderFoot UI and API accessible via HTTPS with basic auth

### Features

- [ ] Bootstrap script (system deps, deploy user, SpiderFoot install) `M`
- [ ] systemd service configuration (auto-restart, logging) `S`
- [ ] Nginx reverse proxy with Let's Encrypt HTTPS `S`
- [ ] Basic auth via passwd file `XS`
- [ ] GitHub Actions deploy workflow (SSH + deploy.sh) `M`
- [ ] Firewall hardening (UFW: block port 5001 externally) `XS`
- [ ] Deploy verification (health check in CI) `S`

### Dependencies

- Hetzner VPS provisioned with Ubuntu 24.04 LTS
- SSH key added at VPS creation
- GitHub Secrets configured (SSH key, host, domain, auth credentials)

## Phase 2: OSINT Module Configuration

**Goal:** Configure SpiderFoot modules with relevant API keys for UHNW profiling
**Success Criteria:** A test scan on a known name returns structured results from at least 3 data sources

### Features

- [ ] OpenCorporates API key integration `XS`
- [ ] Pappers API key integration `XS`
- [ ] Exa.ai API key integration `XS`
- [ ] IntelX API key integration `XS`
- [ ] Module selection tuning for UHNW profiles `S`
- [ ] Test scan validation and result quality review `S`

### Dependencies

- Phase 1 complete
- API keys obtained for each service

## Phase 3: Simple Async API

**Goal:** Expose a minimal API that wraps SpiderFoot — submit a query, poll for results
**Success Criteria:** POST a target, receive a scan ID, GET results when ready; consumers decide how to use it

### Features

- [ ] POST /scans — submit a target (name, domain, company), returns scan ID `S`
- [ ] GET /scans/:id — poll scan status (pending, running, complete, failed) `S`
- [ ] GET /scans/:id/results — retrieve raw SpiderFoot results when complete `S`
- [ ] API authentication (API key or basic auth) `XS`
- [ ] Lightweight wrapper service (Flask or FastAPI) over SpiderFoot REST API `M`

### Dependencies

- Phase 2 complete

## Phase 4: AI Synthesis & Report Generation

**Goal:** Feed scan results through Claude to produce structured UHNW prospect reports
**Success Criteria:** GET /scans/:id/report returns an AI-synthesized intelligence brief

### Features

- [ ] Claude synthesis prompt (SpiderFoot JSON to structured UHNW brief) `M`
- [ ] GET /scans/:id/report — returns AI-synthesized report `S`
- [ ] Report formatting (markdown / HTML) `S`
- [ ] PDF export option `M`

### Dependencies

- Phase 3 complete
- Claude API access

## Phase 5: Compliance & Network Intelligence

**Goal:** Add automated compliance screening and network-based prospect discovery
**Success Criteria:** Compliance report generated per scan; network graph surfaces at least 2 connected prospects per target

### Features

- [ ] PEP screening automation `M`
- [ ] Sanctions list cross-referencing (OFAC, EU) `M`
- [ ] Adverse media check pipeline `M`
- [ ] Beneficial ownership chain resolution `L`
- [ ] Network mapping (co-directors, co-investors, family) `L`
- [ ] Timing signal detection (liquidity events) `M`

### Dependencies

- Phase 4 complete
- Access to PEP and sanctions databases

## Phase 6: Aston Platform Integration (Future)

**Goal:** Connect Aston Rails app to OSINT platform if volume and workflow justify it
**Success Criteria:** Aston user submits a name via in-app form, receives a report within the Aston UI

### Features

- [ ] Rails wrapper: form to POST /api/scan/new `M`
- [ ] Result storage and retrieval in Aston `S`
- [ ] In-app report display `M`

### Dependencies

- Phase 5 complete
- Decision to integrate (DEC-TBD)

## Phase 7: Scale, Compliance & Enterprise

**Goal:** Production hardening, RGPD compliance, and multi-user access
**Success Criteria:** Platform passes internal compliance audit; supports concurrent users with role-based access

### Features

- [ ] RGPD compliance review and data retention policy `L`
- [ ] Legitimate interest documentation `M`
- [ ] Role-based access control `M`
- [ ] Audit logging for all scans and report access `M`
- [ ] Automated scan scheduling for portfolio monitoring `L`
- [ ] Performance optimization for concurrent scans `M`

### Dependencies

- Phase 6 complete (or standalone if integration deferred)
- Legal review of RGPD obligations
