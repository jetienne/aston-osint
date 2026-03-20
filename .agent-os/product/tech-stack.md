# Technical Stack

Language: Python 3.12+
Web Framework: FastAPI
Async Runtime: asyncio (parallel source queries)
HTTP Client: httpx (async)
PDF Generation: WeasyPrint
AI Synthesis: Claude API (Anthropic SDK)
Containerisation: Docker
Server: Hetzner VPS, Ubuntu 24.04 LTS
Reverse Proxy: Nginx
TLS Certificates: Let's Encrypt via Certbot (auto-renewing)
Authentication: API key (header-based)
CI/CD Platform: GitHub Actions (manual trigger, workflow_dispatch)
Deployment Method: Docker build + SSH deploy
Code Repository: git@github.com:jetienne/aston-osint.git
Ops Web Form: Static HTML served by nginx (no framework, no build step)

Data Sources:
- OCCRP Aleph: REST API, free, no key required
- OpenSanctions: REST API, free tier
- ICIJ OffshoreLeaks: REST API, free, no key required
- Pappers: REST API, free tier (limited)
- GDELT: REST API, free, no key required
