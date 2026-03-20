# Technical Stack

OSINT Engine: SpiderFoot (Python, self-hosted)
Runtime: Python 3 + pip
Operating System: Ubuntu 24.04 LTS
Server Provider: Hetzner VPS
Reverse Proxy: Nginx
TLS Certificates: Let's Encrypt via Certbot (auto-renewing)
Authentication: Basic auth via passwd file
Process Manager: systemd (Restart=always)
CI/CD Platform: GitHub Actions
CI/CD Trigger: Push to main branch
Deployment Method: SSH + deploy script (GitOps)
Code Repository: git@github.com:jetienne/aston-osint.git
Firewall: UFW (ports 22, 80, 443 only; SpiderFoot port 5001 blocked externally)
API Layer: Flask or FastAPI (lightweight wrapper over SpiderFoot REST API)
AI Synthesis: Claude API (structured UHNW prospect briefs from SpiderFoot JSON)
Report Format: Markdown/HTML with optional PDF export
Future Integration: Rails/Aston app connection deferred — standalone async API for now
