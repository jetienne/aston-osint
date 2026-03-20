# Spec Requirements Document

> Spec: GitOps Infrastructure
> Created: 2026-03-20
> Status: Planning

## Overview

Deploy SpiderFoot as a self-hosted OSINT engine on a Hetzner VPS, fully managed via a GitOps workflow. A single git push to main triggers automated deployment via GitHub Actions. No manual SSH commands after initial server bootstrap.

## User Stories

### One-Command Server Bootstrap

As a tech lead, I want to run a single bootstrap script on a fresh Hetzner VPS, so that SpiderFoot is installed, configured, and accessible via HTTPS without manual step-by-step setup.

The tech lead creates a Hetzner VPS with Ubuntu 24.04 LTS and an SSH key. They SSH in once, run `bootstrap.sh` as root, and the script installs all dependencies (Python 3, pip, git, nginx, certbot), creates a deploy user, clones SpiderFoot, installs its requirements, configures systemd and nginx, obtains a TLS certificate, and verifies the service is reachable on HTTPS.

### Push-to-Deploy Updates

As a developer, I want to push code to the main branch and have the server automatically update, so that configuration changes and updates are deployed without SSH access.

The developer pushes to main. GitHub Actions connects to the server via SSH and runs `deploy.sh`, which pulls latest code, copies updated config files (nginx.conf, spiderfoot.service), writes the SpiderFoot passwd file from injected secrets, reloads nginx, restarts the SpiderFoot systemd service, and verifies the service is running and HTTPS is responding.

### Secure Access

As a compliance officer, I want SpiderFoot to be accessible only via HTTPS with authentication, so that scan data and the OSINT engine are not exposed to unauthorized access.

SpiderFoot runs on localhost:5001, which is blocked externally by UFW. Nginx reverse-proxies HTTPS traffic to localhost:5001 with basic auth enforced. Only ports 22, 80, and 443 are open. TLS certificates auto-renew via certbot.

## Spec Scope

1. **Bootstrap Script** - One-time setup script that installs all dependencies, configures systemd, nginx, and TLS on a fresh Ubuntu 24.04 VPS
2. **Deploy Script** - Idempotent update script that pulls code, applies config, restarts services, and verifies health
3. **GitHub Actions Workflow** - CI/CD pipeline triggered on push to main that SSHs into the server and runs deploy.sh
4. **Nginx Configuration** - Reverse proxy config with basic auth, HTTPS termination, and proxy to localhost:5001
5. **systemd Service** - SpiderFoot service unit with auto-restart, proper logging, and correct user permissions

## Out of Scope

- SpiderFoot module configuration and API key setup (Phase 2)
- Async API wrapper over SpiderFoot (Phase 3)
- Claude AI synthesis and report generation (Phase 4)
- Aston Rails integration
- Dark web / Tor routing
- Multi-server / high-availability setup

## Expected Deliverable

1. Running `bootstrap.sh` on a fresh Hetzner Ubuntu 24.04 VPS results in SpiderFoot accessible at https://SF_DOMAIN with basic auth
2. Pushing to main branch triggers GitHub Actions which deploys config changes and restarts services within 60 seconds
3. SpiderFoot port 5001 is not reachable from the public internet; only HTTPS via nginx is exposed
