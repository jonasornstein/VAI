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

# Type=simple: systemd reports "started" as soon as the process is forked,
# before Python has bound 127.0.0.1:8765. Wait until HTTP answers.
echo "==> Wait for 127.0.0.1:8765"
ready=""
for _ in $(seq 1 50); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 1 http://127.0.0.1:8765/ || true)"
  if [[ "$code" == "200" ]]; then
    ready=1
    break
  fi
  sleep 0.2
done
if [[ -z "$ready" ]]; then
  echo "ERROR: vai.service did not accept HTTP on 127.0.0.1:8765 within 10s" >&2
  journalctl -u vai -n 40 --no-pager >&2 || true
  exit 1
fi
echo "    OK — app is listening"

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

echo "==> Verify user guide (git-deployed HTML)"
if [[ ! -f "$APP_DIR/vai-guide.html" ]]; then
  echo "ERROR: $APP_DIR/vai-guide.html missing after git reset" >&2
  exit 1
fi
if ! grep -q 'Användarguide' "$APP_DIR/vai-guide.html"; then
  echo "ERROR: $APP_DIR/vai-guide.html does not look like the operator guide" >&2
  exit 1
fi
guide_code="$(curl -sS -o /tmp/vai-guide-check.html -w '%{http_code}' http://127.0.0.1:8765/guide.html || true)"
if [[ "$guide_code" != "200" ]]; then
  echo "ERROR: GET /guide.html via app returned HTTP $guide_code (expected 200)" >&2
  exit 1
fi
if ! grep -q 'Användarguide' /tmp/vai-guide-check.html; then
  echo "ERROR: app-served /guide.html missing 'Användarguide'" >&2
  exit 1
fi
rm -f /tmp/vai-guide-check.html
echo "    OK — user guide via app (/guide.html)"

echo "==> Done — https://vai.ornstein.work/  (guide: /guide.html · stats: /vai-stats.html)"