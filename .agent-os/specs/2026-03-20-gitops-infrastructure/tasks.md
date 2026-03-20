# Spec Tasks

## Tasks

- [x] 1. Create repository file structure and configuration files
  - [x] 1.1 Create `config/spiderfoot.service` systemd unit file
  - [x] 1.2 Create `config/nginx.conf` with reverse proxy, basic auth, and WebSocket support
  - [x] 1.3 Verify config files have correct syntax and placeholders

- [x] 2. Create bootstrap script
  - [x] 2.1 Create `scripts/bootstrap.sh` — system update, dependency install
  - [x] 2.2 Add deploy user creation with SSH key copy
  - [x] 2.3 Add SpiderFoot clone, venv creation, pip install
  - [x] 2.4 Add systemd service install and enable
  - [x] 2.5 Add nginx config install, default site removal, certbot TLS
  - [x] 2.6 Add UFW firewall configuration (22, 80, 443 only)
  - [x] 2.7 Add final health check (verify HTTPS responds)

- [x] 3. Create deploy script
  - [x] 3.1 Create `scripts/deploy.sh` — git pull, config copy, passwd write
  - [x] 3.2 Add systemd daemon-reload and service restart
  - [x] 3.3 Add nginx config test and reload
  - [x] 3.4 Add health check (curl HTTPS with basic auth returns 200)

- [x] 4. Create GitHub Actions deploy workflow
  - [x] 4.1 Create `.github/workflows/deploy.yml` triggered on push to main
  - [x] 4.2 Add SSH connection step using secrets
  - [x] 4.3 Add deploy.sh execution and exit code verification

- [ ] 5. End-to-end verification
  - [ ] 5.1 Verify bootstrap.sh runs cleanly on a fresh Ubuntu 24.04 VPS
  - [ ] 5.2 Verify SpiderFoot UI accessible at https://SF_DOMAIN with basic auth
  - [ ] 5.3 Verify SpiderFoot REST API accessible at https://SF_DOMAIN/api
  - [ ] 5.4 Verify port 5001 is not reachable from public internet
  - [ ] 5.5 Verify push to main triggers GitHub Actions and deploys in under 60 seconds
  - [ ] 5.6 Verify SpiderFoot auto-restarts after process kill (systemd Restart=always)
