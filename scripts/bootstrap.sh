#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "Error: bootstrap.sh must be run as root"
  exit 1
fi

SF_DOMAIN="${SF_DOMAIN:?Error: SF_DOMAIN environment variable is required}"
CERT_EMAIL="${CERT_EMAIL:?Error: CERT_EMAIL environment variable is required}"
DEPLOY_PUBLIC_KEY="${DEPLOY_PUBLIC_KEY:-}"
REPO_URL="${REPO_URL:-https://github.com/jetienne/aston-osint.git}"

echo "==> System update"
apt update && apt upgrade -y

echo "==> Installing base dependencies"
apt install -y git nginx certbot python3-certbot-nginx curl ca-certificates

echo "==> Installing Docker"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "==> Creating deploy user"
if ! id -u deploy &>/dev/null; then
  adduser --disabled-password --gecos "" deploy
  usermod -aG sudo deploy
  usermod -aG docker deploy
  echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy
fi
mkdir -p /home/deploy/.ssh
if [ -n "$DEPLOY_PUBLIC_KEY" ]; then
  echo "$DEPLOY_PUBLIC_KEY" > /home/deploy/.ssh/authorized_keys
elif [ -f /root/.ssh/authorized_keys ]; then
  cp /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
else
  echo "Error: No SSH public key available for deploy user"
  exit 1
fi
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

echo "==> Cloning aston-osint repo"
if [ ! -d /opt/aston-osint ]; then
  git clone "$REPO_URL" /opt/aston-osint
fi
chown -R deploy:deploy /opt/aston-osint

echo "==> Configuring nginx"
rm -f /etc/nginx/sites-enabled/*
rm -f /etc/nginx/sites-available/aston-osint
rm -f /etc/nginx/sites-available/spiderfoot
cp /opt/aston-osint/config/nginx.conf /etc/nginx/sites-available/aston-osint
ln -sf /etc/nginx/sites-available/aston-osint /etc/nginx/sites-enabled/aston-osint
sed -i "s/SF_DOMAIN/${SF_DOMAIN}/g" /etc/nginx/sites-available/aston-osint

echo "==> Testing nginx config before certbot"
nginx -t && systemctl reload nginx

echo "==> Obtaining TLS certificate"
certbot --nginx -d "$SF_DOMAIN" --non-interactive --agree-tos -m "$CERT_EMAIL"

echo "==> Configuring firewall"
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Reloading nginx"
nginx -t && systemctl reload nginx

echo "==> Health check"
sleep 2
if curl -sf "https://${SF_DOMAIN}" -o /dev/null; then
  echo "==> Nginx is running at https://${SF_DOMAIN}"
else
  echo "Warning: Health check failed. Nginx may still be starting up."
  echo "Check with: systemctl status nginx"
fi

echo "==> Setup complete"
