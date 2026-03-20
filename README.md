# Aston OSINT

Self-hosted OSINT platform for Aston's luxury brand teams. Query a target via chat, SpiderFoot runs the scan, Claude synthesizes results into a structured UHNW prospect report. Covers profiling, AML/KYC compliance, and sales intelligence.

## Why

Standard CRM enrichment tools don't work for UHNW clients. Their wealth sits across holding companies, family offices, and trusts in multiple jurisdictions. Third-party intelligence firms charge EUR 5K+ per report. Aston OSINT brings this capability in-house at marginal cost per profile.

## What It Does

- **UHNW Profiling** — Reconstruct wealth structures from company registries, property records, press mentions, legal filings
- **AML/KYC Compliance** — PEP screening, sanctions cross-referencing (OFAC, EU), adverse media checks, beneficial ownership verification
- **Sales Intelligence** — Direct contact recovery, network mapping of connected prospects, timing signals from liquidity events

## Architecture

- **OSINT Engine:** SpiderFoot (Python, self-hosted)
- **Server:** Hetzner VPS, Ubuntu 24.04 LTS
- **Reverse Proxy:** Nginx + Let's Encrypt HTTPS (auto-renewing)
- **Auth:** Basic auth via passwd file
- **Process Manager:** systemd (auto-restart)
- **CI/CD:** GitHub Actions — `git push main` triggers automated deployment
- **Firewall:** UFW (ports 22, 80, 443 only; SpiderFoot port 5001 blocked externally)

## Deployment

### Initial Setup (once)

1. Create Hetzner VPS — Ubuntu 24.04 LTS, add SSH public key at creation
2. SSH into the server and run `bootstrap.sh` as root
3. Add GitHub Secrets to the repository (`SSH_PRIVATE_KEY`, `SSH_HOST`, `SF_DOMAIN`, `SF_AUTH_USER`, `SF_AUTH_PASS`)
4. Push to `main` — GitHub Actions takes over for all subsequent deploys

### On Every Push to Main

GitHub Actions connects via SSH and runs `deploy.sh`, which:
- Pulls latest code
- Copies updated config files (nginx, systemd)
- Writes SpiderFoot passwd file from secrets
- Reloads nginx and restarts the SpiderFoot service
- Verifies the service is running and HTTPS is responding

## How It Works

Aston OSINT exposes a simple async API over SpiderFoot:

1. **POST /scans** — submit a target (name, company, domain), get a scan ID back
2. **GET /scans/:id** — poll scan status (pending, running, complete, failed)
3. **GET /scans/:id/results** — retrieve raw OSINT results when complete
4. **GET /scans/:id/report** — (future) AI-synthesized prospect report via Claude

Scans can take minutes — the async model lets any consumer (chat, script, future Rails app) integrate without blocking.

## Roadmap

1. **GitOps Infrastructure** — Bootstrap, systemd, nginx, GitHub Actions deploy pipeline
2. **OSINT Module Configuration** — API keys for OpenCorporates, Pappers, Exa.ai, IntelX
3. **Simple Async API** — POST /scans, GET status/results (Flask or FastAPI wrapper)
4. **AI Synthesis & Reports** — Claude-powered prospect briefs, PDF export
5. **Compliance & Network Intelligence** — PEP, sanctions, beneficial ownership, network mapping
6. **Aston Integration** — Rails connection (deferred, if volume justifies)
7. **Scale & RGPD** — Data retention policy, RBAC, audit logging
