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

echo "==> Verify activity stats page (git-deployed HTML)"
if [[ ! -f "$APP_DIR/vai-stats.html" ]]; then
  echo "ERROR: $APP_DIR/vai-stats.html missing after git reset" >&2
  exit 1
fi
if ! grep -q 'Lookup IPs' "$APP_DIR/vai-stats.html"; then
  echo "ERROR: $APP_DIR/vai-stats.html does not look like the IP-lookup viewer" >&2
  exit 1
fi
# App must serve the page (nginx proxies / to the service — no separate static alias).
stats_code="$(curl -sS -o /tmp/vai-stats-check.html -w '%{http_code}' http://127.0.0.1:8765/vai-stats.html || true)"
if [[ "$stats_code" != "200" ]]; then
  echo "ERROR: GET /vai-stats.html via app returned HTTP $stats_code (expected 200)" >&2
  exit 1
fi
if ! grep -q 'Lookup IPs' /tmp/vai-stats-check.html; then
  echo "ERROR: app-served /vai-stats.html missing 'Lookup IPs'" >&2
  exit 1
fi
rm -f /tmp/vai-stats-check.html
echo "    OK — activity stats via app (IP lookup viewer)"

echo "==> Done — https://vai.ornstein.work/  (stats: https://vai.ornstein.work/vai-stats.html)"