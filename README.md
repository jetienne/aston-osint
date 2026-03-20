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
- **CI/CD:** GitHub Actions — manual trigger (switchable to push-to-main later)
- **Firewall:** UFW (ports 22, 80, 443 only; SpiderFoot port 5001 blocked externally)

## Setup (one-time, manual)

No SSH required. You set up 3 things manually, then GitHub Actions handles everything else.

### 1. Create Hetzner VPS

- OS: Ubuntu 24.04 LTS
- Add your SSH public key at creation time (Hetzner UI lets you do this)
- Note the server IP

### 2. Point your domain

Add a DNS A record pointing your chosen domain to the server IP. Wait for propagation before running the bootstrap.

### 3. Add GitHub Secrets

Go to **github.com/jetienne/aston-osint → Settings → Secrets and variables → Actions** and add:

| Secret | What to put | How to get it |
|---|---|---|
| `SSH_ROOT_KEY` | Root SSH private key | The private key matching the public key you added at VPS creation |
| `SSH_HOST` | Server IP address | Hetzner dashboard → your server → Networking |
| `SF_DOMAIN` | Your domain | The domain you pointed in step 2 (e.g. `osint.aston.com`) |
| `CERT_EMAIL` | Email address | Used by Let's Encrypt for certificate notifications |
| `SF_AUTH_USER` | Username | Choose any username for SpiderFoot basic auth |
| `SF_AUTH_PASS` | Password | Choose a strong password for SpiderFoot basic auth |
| `GH_PAT` | GitHub Personal Access Token | Create at github.com/settings/tokens — needs `repo` scope (the bootstrap uses it to auto-save the deploy key as a secret) |

## Deployment (Full GitOps)

Both workflows are triggered manually from the **Actions** tab.

### Bootstrap (once)

Go to **Actions → Bootstrap Server → Run workflow**.

This will:
- SSH as root into the server
- Install Python 3, nginx, certbot, SpiderFoot
- Create a `deploy` user with a freshly generated SSH keypair
- Configure systemd, nginx reverse proxy, Let's Encrypt TLS, UFW firewall
- Save the deploy private key as the `SSH_PRIVATE_KEY` GitHub secret automatically

### Deploy (on demand)

Go to **Actions → Deploy SpiderFoot → Run workflow**.

This will:
- SSH as `deploy` user into the server
- Pull latest code from the repo
- Copy updated config files (nginx, systemd)
- Write the SpiderFoot passwd file from secrets
- Reload nginx and restart the SpiderFoot service
- Verify the service is running and HTTPS is responding

Once stable, the deploy workflow can be switched to trigger on every push to main.

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
