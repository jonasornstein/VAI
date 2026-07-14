#!/usr/bin/env bash
# VAI — first-time install on Ubuntu 22.04/24.04 (Hetzner or similar).
# Run as root: bash deploy/install-ubuntu.sh
set -euo pipefail

APP_USER=vai
APP_DIR=/opt/vai
REPO_URL="${VAI_REPO_URL:-https://github.com/jonasornstein/VAI.git}"
SERVER_NAME="${VAI_SERVER_NAME:-_}"

echo "==> Installing system packages"
apt-get update
apt-get install -y git python3 python3-venv python3-pip nginx

echo "==> Creating service user"
if ! id "$APP_USER" &>/dev/null; then
  useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi

echo "==> Cloning or updating repo at $APP_DIR"
if [[ -d "$APP_DIR/.git" ]]; then
  sudo -u "$APP_USER" git -C "$APP_DIR" pull --ff-only
else
  mkdir -p "$APP_DIR"
  chown "$APP_USER:$APP_USER" "$APP_DIR"
  sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
fi

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
echo "    Logs:    journalctl -u vai -f"
echo "    URL:     http://$SERVER_NAME/  (or http://<server-ip>/)"