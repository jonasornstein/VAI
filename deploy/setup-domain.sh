#!/usr/bin/env bash
# Configure nginx + Let's Encrypt for https://vai.ornstein.work
# Run as root on the Hetzner server after VAI is installed and DNS is set.
set -euo pipefail

DOMAIN="${VAI_DOMAIN:-vai.ornstein.work}"
APP_DIR="${VAI_APP_DIR:-/opt/vai}"
EMAIL="${VAI_CERT_EMAIL:-}"

if [[ -z "$EMAIL" ]]; then
  echo "Set VAI_CERT_EMAIL for Let's Encrypt expiry notices, e.g.:" >&2
  echo "  export VAI_CERT_EMAIL=you@ornstein.work" >&2
  exit 1
fi

if ! systemctl is-active --quiet vai; then
  echo "ERROR: vai service is not running. Run install-ubuntu.sh first." >&2
  exit 1
fi

echo "==> Installing certbot"
apt-get update
apt-get install -y certbot python3-certbot-nginx

echo "==> Nginx HTTP vhost for $DOMAIN (certbot will add HTTPS)"
sed "s/SERVER_NAME/$DOMAIN/" "$APP_DIR/deploy/nginx-vai.conf" > /etc/nginx/sites-available/vai
ln -sf /etc/nginx/sites-available/vai /etc/nginx/sites-enabled/vai
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> Obtaining TLS certificate"
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect

echo "==> Done"
echo "    URL: https://$DOMAIN/"
echo "    Renew: certbot renew (systemd timer installed automatically)"