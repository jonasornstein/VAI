#!/usr/bin/env bash
# Weekly vai backup: consistent SQLite copies (if any) + data dirs -> tar.gz, keep 8, upload to Drive.
# Env: SRC (/opt/vai) DEST (~/backups/vai) KEEP (8) RCLONE (~/bin/rclone) REMOTE (gdrive: = Drive-mappen vai-backup via root_folder_id) DRY_RUN=1 skips upload.
set -euo pipefail
SRC=${SRC:-/opt/vai}; DEST=${DEST:-$HOME/backups/vai}; KEEP=${KEEP:-8}
RCLONE=${RCLONE:-$HOME/bin/rclone}; REMOTE=${REMOTE:-gdrive:}
TS=$(date +%Y-%m-%d_%H%M); WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
mkdir -p "$DEST"; echo "[vai-backup] start $TS src=$SRC"
# 1) Consistent SQLite snapshots
mkdir -p "$WORK/db"
find "$SRC" -xdev \( -path "$SRC/.venv" -o -path "$SRC/.cache" -o -path "$SRC/.git" \) -prune -o \
  -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -print0 |
while IFS= read -r -d '' f; do
  out="$WORK/db/${f#$SRC/}"; mkdir -p "$(dirname "$out")"
  python3 - "$f" "$out" <<'P'
import sqlite3,sys
s=sqlite3.connect(f"file:{sys.argv[1]}?mode=ro",uri=True); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close(); s.close()
P
  echo "[vai-backup] sqlite snapshot: $f"
done
# 2) Archive data + snapshots (excluding venv/caches/live db files)
ARCH="$DEST/vai-$TS.tar.gz"
tar -czf "$ARCH" --warning=no-file-changed \
  --exclude=.venv --exclude=.cache --exclude=.pytest_cache --exclude='*.db' --exclude='*.db-wal' --exclude='*.db-shm' \
  --exclude='*.sqlite*' -C "$(dirname "$SRC")" "$(basename "$SRC")" -C "$WORK" db
echo "[vai-backup] archive $ARCH $(du -h "$ARCH" | cut -f1)"
# 3) Rotation
ls -1t "$DEST"/vai-*.tar.gz | tail -n +$((KEEP+1)) | xargs -r rm -v --
# 4) Upload
if [ "${DRY_RUN:-0}" = 1 ]; then echo "[vai-backup] DRY_RUN: upload skipped"
elif [ -x "$RCLONE" ] && "$RCLONE" listremotes | grep -q "^${REMOTE%%:*}:"; then
  "$RCLONE" copy "$ARCH" "$REMOTE" && echo "[vai-backup] uploaded to $REMOTE"
  "$RCLONE" delete "$REMOTE" --min-age 60d --include 'vai-*.tar.gz' || true
else echo "[vai-backup] WARN: rclone remote ${REMOTE%%:*} not configured, local only"; fi
echo "[vai-backup] done"
