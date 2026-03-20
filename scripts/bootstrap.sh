#!/usr/bin/env bash
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "Error: bootstrap.sh must be run as root"
  exit 1
fi

SF_DOMAIN="${SF_DOMAIN:?Error: SF_DOMAIN environment variable is required}"
CERT_EMAIL="${CERT_EMAIL:?Error: CERT_EMAIL environment variable is required}"
SF_AUTH_USER="${SF_AUTH_USER:?Error: SF_AUTH_USER environment variable is required}"
SF_AUTH_PASS="${SF_AUTH_PASS:?Error: SF_AUTH_PASS environment variable is required}"
DEPLOY_PUBLIC_KEY="${DEPLOY_PUBLIC_KEY:-}"
REPO_URL="${REPO_URL:-https://github.com/jetienne/aston-osint.git}"

echo "==> System update"
apt update && apt upgrade -y

echo "==> Installing dependencies"
apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx apache2-utils curl

echo "==> Creating deploy user"
if ! id -u deploy &>/dev/null; then
  adduser --disabled-password --gecos "" deploy
  usermod -aG sudo deploy
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

echo "==> Cloning SpiderFoot"
if [ ! -d /opt/spiderfoot ]; then
  git clone https://github.com/smicallef/spiderfoot.git /opt/spiderfoot
fi
chown -R deploy:deploy /opt/spiderfoot

echo "==> Installing SpiderFoot dependencies"
python3 -m venv /opt/spiderfoot/venv
/opt/spiderfoot/venv/bin/pip install -r /opt/spiderfoot/requirements.txt

echo "==> Cloning aston-osint repo"
if [ ! -d /opt/aston-osint ]; then
  git clone "$REPO_URL" /opt/aston-osint
fi
chown -R deploy:deploy /opt/aston-osint

echo "==> Configuring systemd service"
cp /opt/aston-osint/config/spiderfoot.service /etc/systemd/system/spiderfoot.service
systemctl daemon-reload
systemctl enable spiderfoot
systemctl start spiderfoot

echo "==> Configuring nginx"
rm -f /etc/nginx/sites-enabled/default
cp /opt/aston-osint/config/nginx.conf /etc/nginx/sites-available/spiderfoot
ln -sf /etc/nginx/sites-available/spiderfoot /etc/nginx/sites-enabled/spiderfoot

# Replace SF_DOMAIN placeholder in nginx config
sed -i "s/SF_DOMAIN/${SF_DOMAIN}/g" /etc/nginx/sites-available/spiderfoot

echo "==> Setting up basic auth"
htpasswd -cb /etc/nginx/.htpasswd "$SF_AUTH_USER" "$SF_AUTH_PASS"

echo "==> Obtaining TLS certificate"
nginx -t && systemctl reload nginx
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
if curl -sf -u "${SF_AUTH_USER}:${SF_AUTH_PASS}" "https://${SF_DOMAIN}" -o /dev/null; then
  echo "==> SpiderFoot is running at https://${SF_DOMAIN}"
else
  echo "Warning: Health check failed. SpiderFoot may still be starting up."
  echo "Check with: systemctl status spiderfoot"
fi

echo "==> Bootstrap complete"
