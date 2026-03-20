#!/usr/bin/env bash
set -euo pipefail

SF_DOMAIN="${SF_DOMAIN:?Error: SF_DOMAIN environment variable is required}"
SF_AUTH_USER="${SF_AUTH_USER:?Error: SF_AUTH_USER environment variable is required}"
SF_AUTH_PASS="${SF_AUTH_PASS:?Error: SF_AUTH_PASS environment variable is required}"

REPO_DIR="/opt/aston-osint"

echo "==> Pulling latest code"
cd "$REPO_DIR"
git fetch origin main
git reset --hard origin/main

echo "==> Updating systemd service"
sudo cp config/spiderfoot.service /etc/systemd/system/spiderfoot.service
sudo systemctl daemon-reload

echo "==> Updating basic auth"
sudo htpasswd -cb /etc/nginx/.htpasswd "$SF_AUTH_USER" "$SF_AUTH_PASS"

echo "==> Restarting SpiderFoot"
sudo systemctl restart spiderfoot

echo "==> Reloading nginx"
sudo nginx -t && sudo systemctl reload nginx

echo "==> Health check"
sleep 2
if curl -sf -u "${SF_AUTH_USER}:${SF_AUTH_PASS}" "https://${SF_DOMAIN}" -o /dev/null; then
  echo "==> Deploy successful — SpiderFoot running at https://${SF_DOMAIN}"
else
  echo "Error: Health check failed"
  sudo systemctl status spiderfoot --no-pager
  exit 1
fi
