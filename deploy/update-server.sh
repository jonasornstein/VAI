#!/usr/bin/env bash
# Update VAI on the Hetzner server — run as root.
set -euo pipefail

APP_DIR=/opt/vai
BRANCH="${VAI_BRANCH:-master}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/update-server.sh" >&2
  exit 1
fi

echo "==> Fetch $BRANCH"
sudo -u vai git -C "$APP_DIR" fetch origin "$BRANCH"

echo "==> Reset to origin/$BRANCH (discards local server-only drift)"
sudo -u vai git -C "$APP_DIR" checkout "$BRANCH"
sudo -u vai git -C "$APP_DIR" reset --hard "origin/$BRANCH"

echo "==> Reinstall package"
sudo -u vai "$APP_DIR/.venv/bin/pip" install -e "$APP_DIR"

echo "==> Restart service"
systemctl restart vai
systemctl status vai --no-pager

echo "==> Done — https://vai.ornstein.work/"