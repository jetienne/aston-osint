# Aston OSINT

Self-hosted intelligence pipeline for Aston's luxury brand teams. Submit a name, get a structured UHNW prospect brief — PDF and JSON — by aggregating 5 open-source data sources and synthesising with Claude. Covers AML/KYC compliance and sales intelligence.

## Why

Aston handles villa and chalet transactions from EUR 20K to EUR 500K+ with UHNW clients. No systematic screening exists. Third-party intelligence firms charge EUR 2K-5K per report. This pipeline replaces manual research with an automated, auditable process at zero marginal cost per query.

## Data Sources

| Source | What it provides | Auth |
|---|---|---|
| OCCRP Aleph | Investigations, court records, corporate registries, leaks | Free, no key |
| OpenSanctions | PEP lists, sanctions (OFAC, EU, UN), watchlists | Free tier |
| ICIJ OffshoreLeaks | Panama Papers, Paradise Papers, offshore entities | Free, no key |
| Pappers | French company registries, beneficial ownership | Free tier |
| GDELT | Global news and event monitoring | Free, no key |

## How It Works

1. Ops submits a name via web form or `POST /api/v1/scan`
2. FastAPI orchestrator fans out to 5 sources in parallel (30s timeout each)
3. Aggregated results sent to Claude API with structured synthesis prompt
4. Claude returns a brief: identity, entities, sanctions flags, offshore links, press signals, risk score
5. WeasyPrint renders a PDF from an HTML template
6. Response: `{ brief: {...}, pdf_base64: '...', sources_hit: [...], duration_ms: ... }`

## Architecture

- **Pipeline:** FastAPI + asyncio (Python 3.12+)
- **Data Sources:** OCCRP Aleph, OpenSanctions, ICIJ OffshoreLeaks, Pappers, GDELT
- **AI Synthesis:** Claude API (Anthropic SDK)
- **PDF Generation:** WeasyPrint
- **Deployment:** Docker on Hetzner VPS
- **Reverse Proxy:** Nginx + Let's Encrypt HTTPS
- **Auth:** API key (header-based)
- **CI/CD:** GitHub Actions (manual trigger)
- **Ops UI:** Static HTML form served by nginx

## Setup (one-time, manual)

No SSH required. You set up 3 things manually, then GitHub Actions handles everything else.

### 1. Create Hetzner VPS

- OS: Ubuntu 24.04 LTS
- Add your SSH public key at creation time (Hetzner UI lets you do this)
- Note the server IP

### 2. Point your domain

Add a DNS A record pointing `osint.aston.app` to the server IP. Wait for propagation before running setup.

### 3. Add Environment Secrets

Go to **github.com/jetienne/aston-osint → Settings → Environments**, select `production`, then add these secrets:

| Secret | What to put | How to get it |
|---|---|---|
| `SSH_ROOT_KEY` | Root SSH private key | The private key matching the public key you added at VPS creation |
| `SSH_HOST` | Server IP address | Hetzner dashboard → your server → Networking |
| `SF_DOMAIN` | `osint.aston.app` | The domain you pointed in step 2 |
| `CERT_EMAIL` | Email address | Used by Let's Encrypt for certificate notifications |
| `API_KEY` | API key for scan endpoint | Choose a strong random string |
| `ANTHROPIC_API_KEY` | Claude API key | From console.anthropic.com |

## Deployment (Full GitOps)

Both workflows are triggered manually from the **Actions** tab.

### Setup VPS (once)

Go to **Actions → Setup VPS → Run workflow**.

This will:
- SSH as root into the server
- Install Docker, nginx, certbot
- Create a `deploy` user with a freshly generated SSH keypair
- Configure nginx reverse proxy, Let's Encrypt TLS, UFW firewall
- Print the deploy private key in the workflow logs

After setup completes, copy the private key from the logs and add it as the `SSH_PRIVATE_KEY` secret in the `production` environment. The deploy workflow uses this key to connect as the `deploy` user.

### Deploy (on demand)

Go to **Actions → Deploy → Run workflow**.

This will:
- SSH as `deploy` user into the server
- Build and restart the Docker container
- Verify the service is running and HTTPS is responding

## Roadmap

1. **GitOps Infrastructure** — Docker, nginx, GitHub Actions deploy pipeline
2. **Source Adapters** — Async adapters for all 5 data sources
3. **Claude Synthesis & Reports** — AI brief generation, PDF output, POST /api/v1/scan
4. **Ops Web Form** — Simple HTML form for non-technical users
5. **Aston Integration** — Rails connection (deferred)
6. **Monitoring & Extended Sources** — Re-screening, alerting, Companies House, OpenCorporates
