#!/usr/bin/env bash
set -euo pipefail

SF_DOMAIN="${SF_DOMAIN:?Error: SF_DOMAIN environment variable is required}"

REPO_DIR="/opt/aston-osint"

git config --global --add safe.directory /opt/aston-osint

echo "==> Pulling latest code"
cd "$REPO_DIR"
git fetch origin main
git reset --hard origin/main

echo "==> Building Docker image"
docker build -t aston-osint .

echo "==> Stopping existing container"
docker stop aston-osint 2>/dev/null || true
docker rm aston-osint 2>/dev/null || true

echo "==> Starting container"
DOCKER_ARGS="-d --name aston-osint --restart unless-stopped -p 127.0.0.1:8000:8000"
if [ -f /opt/aston-osint/.env ]; then
  DOCKER_ARGS="$DOCKER_ARGS --env-file /opt/aston-osint/.env"
fi
docker run $DOCKER_ARGS aston-osint

echo "==> Reloading nginx"
nginx -t && systemctl reload nginx

echo "==> Health check"
sleep 3
if curl -sf "https://${SF_DOMAIN}/health" -o /dev/null; then
  echo "==> Deploy successful — Aston OSINT running at https://${SF_DOMAIN}"
else
  echo "Error: Health check failed"
  docker logs aston-osint --tail 20
  exit 1
fi
