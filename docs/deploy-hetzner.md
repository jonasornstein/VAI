# VAI — Hetzner deployment (ornstein)

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Owner** | ornstein |
| **Last updated** | 2026-07-15 |
| **Production URL** | https://vai.ornstein.work/ |
| **Server** | Hetzner Ubuntu — `168.119.155.11` (`dev-server`) |
| **GitHub** | https://github.com/jonasornstein/VAI.git (public, branch `master`) |

Operator guide for deploying and updating VAI on the Hetzner server. **Production hosting is Hetzner only** (no Vercel). Scripts live in [`deploy/`](../deploy/).

---

## Architecture

```
Browser → nginx :443 (TLS) → proxy → python -m vai serve @ 127.0.0.1:8765
```

| Component | Path / name |
|-----------|-------------|
| App install | `/opt/vai` |
| Service user | `vai` |
| Python venv | `/opt/vai/.venv` |
| systemd unit | `vai.service` |
| nginx site | `/etc/nginx/sites-available/vai` |
| TLS certs | `/etc/letsencrypt/live/vai.ornstein.work/` |

---

## Prerequisites

- Ubuntu 22.04 or 24.04 on Hetzner
- Root SSH (or Hetzner web console)
- DNS: `A` record `vai.ornstein.work` → `168.119.155.11`
- GitHub repo **public** (so the server can `git clone` without credentials)

---

## First-time install

SSH as **root**. Working directory does not matter — commands use absolute paths.

### 1. Clone and install

```bash
git clone https://github.com/jonasornstein/VAI.git /tmp/vai-install
cd /tmp/vai-install
git checkout master
export VAI_SERVER_NAME=vai.ornstein.work
bash deploy/install-ubuntu.sh
```

This creates `/opt/vai`, installs Python deps, enables `vai.service`, and configures nginx on port 80.

### 2. HTTPS (Let's Encrypt)

```bash
export VAI_CERT_EMAIL=you@ornstein.work
export VAI_DOMAIN=vai.ornstein.work
bash /opt/vai/deploy/setup-domain.sh
```

If HTTPS returns **403** but HTTP works, repair the nginx SSL vhost:

```bash
bash /opt/vai/deploy/fix-nginx-https.sh
```

### 3. Verify

```bash
systemctl status vai
curl -s -o /dev/null -w "%{http_code}\n" https://vai.ornstein.work/
curl -sI https://vai.ornstein.work/ | head -3
```

Expect **`active (running)`** and **`200`** for both curls. Open https://vai.ornstein.work/ in a browser.

---

## Update after pushing to GitHub

Day-to-day: develop and push from the **dev clone** (`/home/ornstein/grok/vai` as `ornstein`), then on the same server run the update with **sudo** (not a daily root shell).

### Standard update (recommended)

```bash
# as ornstein, after: git push origin master
sudo bash /opt/vai/deploy/update-server.sh
```

### Manual update (same steps)

```bash
sudo -u vai git -C /opt/vai fetch origin master
sudo -u vai git -C /opt/vai reset --hard origin/master
sudo -u vai /opt/vai/.venv/bin/pip install -e /opt/vai
sudo systemctl restart vai
```

### Verify after update

```bash
systemctl status vai
curl -s -o /dev/null -w "%{http_code}\n" https://vai.ornstein.work/
```

---

## Rules (learned from production)

| Do | Don't |
|----|-------|
| Run **git** as `sudo -u vai` | Run `git` as **root** in `/opt/vai` (ownership / `safe.directory` errors) |
| Use **`reset --hard origin/master`** on the server | Use `git pull` on the server (branches can diverge) |
| Track branch **`master`** | Clone default `main` without checking out `master` |
| Health check: `curl -s -o /dev/null -w "%{http_code}\n" …` | Rely only on `curl -I` before HEAD support was added (now both return 200) |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `dubious ownership` when root runs git | Use `sudo -u vai git -C /opt/vai …` |
| `Need to specify how to reconcile divergent branches` | `sudo -u vai git -C /opt/vai reset --hard origin/master` |
| HTTPS **403**, HTTP **200** | `bash /opt/vai/deploy/fix-nginx-https.sh` |
| App not responding | `journalctl -u vai -n 30 --no-pager` then `systemctl restart vai` |
| nginx config test | `nginx -t && systemctl reload nginx` |
| TLS renewal | Automatic via certbot timer; manual: `certbot renew` |

---

## Firewall (optional)

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

---

## Local development vs production

Dev and production share the **same Hetzner VM** (`dev-server`), with separate trees and users.

| | Development (workstation) | Production |
|--|---------------------------|------------|
| Host | Same Hetzner VM (`dev-server`) | Same VM |
| Path | `/home/ornstein/grok/vai` | `/opt/vai` |
| User | `ornstein` (sudo when needed) | `vai` (systemd) |
| Start | `python -m vai serve` (venv) | `systemctl start vai` |
| URL | http://127.0.0.1:8765/ | https://vai.ornstein.work/ |
| Update code | work on `master` / `git pull` | `sudo bash /opt/vai/deploy/update-server.sh` |
| Tools | Grok CLI + Git + SSH | nginx + `vai.service` |

**Same VM, separate trees**

- Develop only under `/home/ornstein/grok/vai` — do **not** edit or `git pull` as your daily workflow inside `/opt/vai`.
- Do **not** install the app under `/var/www/html` (VAI is not static files; install and systemd assume `/opt/vai`).

**Ship path**

1. As `ornstein`: develop in `~/grok/vai`, then `git push origin master`.
2. Still as `ornstein`: `sudo bash /opt/vai/deploy/update-server.sh` (script runs git as user `vai`).

**Daily root**

Avoid logging in as root for routine work. Use `ornstein` + `sudo` for deploy; git operations under `/opt/vai` stay as `sudo -u vai` (see [Rules](#rules-learned-from-production)).

---

## Related files

| File | Purpose |
|------|---------|
| [`deploy/install-ubuntu.sh`](../deploy/install-ubuntu.sh) | First-time install |
| [`deploy/setup-domain.sh`](../deploy/setup-domain.sh) | TLS + domain |
| [`deploy/fix-nginx-https.sh`](../deploy/fix-nginx-https.sh) | Fix HTTPS 403 |
| [`deploy/update-server.sh`](../deploy/update-server.sh) | Routine updates |
| [`deploy/vai.service`](../deploy/vai.service) | systemd unit |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.1 | 2026-07-15 | Workstation local-vs-prod — dev `~/grok/vai` as ornstein, prod `/opt/vai` as vai, ship bridge |
| 1.0 | 2026-07-14 | Initial operator doc — Hetzner + vai.ornstein.work production path |