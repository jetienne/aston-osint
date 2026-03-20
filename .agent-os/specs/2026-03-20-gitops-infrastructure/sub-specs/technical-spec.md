# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2026-03-20-gitops-infrastructure/spec.md

## Technical Requirements

### Server

- Hetzner VPS: Ubuntu 24.04 LTS, minimum 2 vCPU / 4 GB RAM
- Firewall: UFW allowing ports 22 (SSH), 80 (HTTP for certbot), 443 (HTTPS) only
- Port 5001 blocked externally (SpiderFoot default)

### Bootstrap Script (bootstrap.sh)

- Run as root on a fresh VPS
- System update: `apt update && apt upgrade -y`
- Install dependencies: python3, python3-pip, python3-venv, git, nginx, certbot, python3-certbot-nginx
- Create deploy user (`deploy`) with sudo privileges and no-password SSH (copy root authorized_keys)
- Clone SpiderFoot to `/opt/spiderfoot` from official repo
- Create Python venv at `/opt/spiderfoot/venv` and install requirements
- Copy `config/spiderfoot.service` to `/etc/systemd/system/`, enable and start
- Copy `config/nginx.conf` to `/etc/nginx/sites-available/spiderfoot`, symlink to sites-enabled, remove default site
- Run `certbot --nginx -d $SF_DOMAIN --non-interactive --agree-tos -m $CERT_EMAIL`
- Configure UFW: deny incoming, allow 22, 80, 443, enable
- Reload nginx, verify SpiderFoot is reachable on HTTPS

### systemd Service (config/spiderfoot.service)

- ExecStart: `/opt/spiderfoot/venv/bin/python3 /opt/spiderfoot/sf.py -l 127.0.0.1:5001`
- User: deploy
- WorkingDirectory: /opt/spiderfoot
- Restart: always
- RestartSec: 5
- Environment: production settings

### Nginx Configuration (config/nginx.conf)

- Listen 443 SSL (managed by certbot)
- Listen 80 redirect to HTTPS (managed by certbot)
- Server name: SF_DOMAIN
- Proxy pass to http://127.0.0.1:5001
- Basic auth via /etc/nginx/.htpasswd
- Proxy headers: X-Real-IP, X-Forwarded-For, X-Forwarded-Proto, Host
- WebSocket support for SpiderFoot UI (Upgrade, Connection headers)

### Deploy Script (scripts/deploy.sh)

- Run as deploy user via SSH
- Pull latest code from git repo
- Copy config/spiderfoot.service to /etc/systemd/system/ (sudo)
- Copy config/nginx.conf to /etc/nginx/sites-available/spiderfoot (sudo)
- Write /etc/nginx/.htpasswd from environment variables (SF_AUTH_USER, SF_AUTH_PASS)
- Reload systemd daemon, restart spiderfoot service (sudo)
- Test nginx config, reload nginx (sudo)
- Health check: curl -sf https://SF_DOMAIN (with basic auth) returns 200

### GitHub Actions Workflow (.github/workflows/deploy.yml)

- Trigger: push to main branch
- Runner: ubuntu-latest
- Steps:
  1. SSH into server as deploy user using SSH_PRIVATE_KEY secret
  2. Run deploy.sh
  3. Verify exit code

### GitHub Secrets Required

- `SSH_PRIVATE_KEY` - deploy user SSH private key
- `SSH_HOST` - server IP or hostname
- `SF_DOMAIN` - SpiderFoot domain name
- `SF_AUTH_USER` - basic auth username
- `SF_AUTH_PASS` - basic auth password
- `CERT_EMAIL` - email for Let's Encrypt registration

## Repository File Structure

```
aston-osint/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── config/
│   ├── nginx.conf
│   └── spiderfoot.service
├── scripts/
│   ├── bootstrap.sh
│   └── deploy.sh
├── .agent-os/
│   └── ...
└── README.md
```
