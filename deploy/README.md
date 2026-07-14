# VAI — Ubuntu server deploy (Hetzner)

Runs `python -m vai serve` behind nginx on port 80. The app binds to `127.0.0.1:8765`; nginx proxies public traffic.

## Prerequisites

- Ubuntu 22.04 or 24.04
- Root SSH access
- GitHub repo cloned (default: `https://github.com/jonasornstein/VAI.git`)

## Quick install (public GitHub repo)

On the server:

```bash
export VAI_REPO_URL=https://github.com/jonasornstein/VAI.git
export VAI_SERVER_NAME=your.domain.example   # or server IP
sudo bash deploy/install-ubuntu.sh
```

## Private repo / no GitHub login

If the repo is private (or you cannot sign in to GitHub), copy the project from your PC — no GitHub on the server.

**On your PC** (PowerShell; you only need Hetzner SSH access):

```powershell
cd "C:\Users\jonte\OneDrive\grok\vai"
tar -czf vai-deploy.tgz --exclude=.git --exclude=__pycache__ --exclude=.venv --exclude=mcps .
scp vai-deploy.tgz root@168.119.155.11:/tmp/
```

**On the Hetzner server** (SSH or web console):

```bash
mkdir -p /opt/vai
tar -xzf /tmp/vai-deploy.tgz -C /opt/vai
export VAI_SERVER_NAME=168.119.155.11
bash /opt/vai/deploy/install-ubuntu-local.sh
```

Then open http://168.119.155.11/

## Manual steps

```bash
# Clone
sudo useradd --system --home-dir /opt/vai --shell /usr/sbin/nologin vai
sudo git clone https://github.com/jonasornstein/VAI.git /opt/vai
sudo chown -R vai:vai /opt/vai

# Python
sudo -u vai python3 -m venv /opt/vai/.venv
sudo -u vai /opt/vai/.venv/bin/pip install -e /opt/vai[dev]

# systemd + nginx
sudo cp /opt/vai/deploy/vai.service /etc/systemd/system/
sudo systemctl enable --now vai
sudo cp /opt/vai/deploy/nginx-vai.conf /etc/nginx/sites-available/vai
# Edit server_name, then:
sudo ln -s /etc/nginx/sites-available/vai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Update after git push

```bash
sudo -u vai git -C /opt/vai pull
sudo -u vai /opt/vai/.venv/bin/pip install -e /opt/vai
sudo systemctl restart vai
```

## Custom domain + HTTPS (vai.ornstein.work)

**DNS:** `A` record `vai` → `168.119.155.11` (already configured).

After `install-ubuntu.sh`, on the server:

```bash
export VAI_CERT_EMAIL=you@ornstein.work
export VAI_DOMAIN=vai.ornstein.work
bash /opt/vai/deploy/setup-domain.sh
```

Opens **https://vai.ornstein.work/** with automatic HTTP→HTTPS redirect.

Manual certbot alternative:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d vai.ornstein.work
```

## Firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```