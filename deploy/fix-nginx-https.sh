#!/usr/bin/env bash
# Fix nginx HTTPS 403 — ensure SSL vhost proxies to VAI (not static root).
set -euo pipefail

DOMAIN="${VAI_DOMAIN:-vai.ornstein.work}"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"

if [[ ! -f "$CERT_DIR/fullchain.pem" ]]; then
  echo "ERROR: TLS cert not found at $CERT_DIR" >&2
  echo "Run: certbot --nginx -d $DOMAIN" >&2
  exit 1
fi

cat > /etc/nginx/sites-available/vai <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate $CERT_DIR/fullchain.pem;
    ssl_certificate_key $CERT_DIR/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 1m;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/vai /etc/nginx/sites-enabled/vai
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

echo "Fixed. Test: curl -sI https://$DOMAIN/ | head -3"