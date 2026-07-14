#!/usr/bin/env bash
# VAI — install from files already on disk (no git / no GitHub).
# Run as root after copying the project to /opt/vai.
set -euo pipefail

APP_USER=vai
APP_DIR=/opt/vai
SERVER_NAME="${VAI_SERVER_NAME:-_}"

if [[ ! -f "$APP_DIR/pyproject.toml" ]]; then
  echo "ERROR: $APP_DIR/pyproject.toml not found. Copy the VAI project there first." >&2
  exit 1
fi

echo "==> Installing system packages"
apt-get update
apt-get install -y python3 python3-venv python3-pip nginx

echo "==> Creating service user"
if ! id "$APP_USER" &>/dev/null; then
  useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "==> Python virtualenv + editable install"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -e "$APP_DIR[dev]"

echo "==> Running tests"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" -m pytest -q "$APP_DIR/tests"

echo "==> Installing systemd unit"
cp "$APP_DIR/deploy/vai.service" /etc/systemd/system/vai.service
systemctl daemon-reload
systemctl enable vai
systemctl restart vai

echo "==> Configuring nginx"
sed "s/SERVER_NAME/$SERVER_NAME/" "$APP_DIR/deploy/nginx-vai.conf" > /etc/nginx/sites-available/vai
ln -sf /etc/nginx/sites-available/vai /etc/nginx/sites-enabled/vai
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> Done"
echo "    Service: systemctl status vai"
echo "    URL:     http://$SERVER_NAME/"