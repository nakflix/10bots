# Deploying the 10 File-Sharing Bots on a VPS

This guide walks through deploying the bundle (`multi-file-sharing-10bots.zip`)
on a fresh Linux VPS (Ubuntu/Debian) using Docker + Docker Compose, running all
10 bots from a single `.env` file.

---

## 1. Requirements

- A VPS running Ubuntu 20.04/22.04/24.04 (or Debian equivalent), at least 1–2GB RAM
- Root or sudo access
- 10 Telegram bot tokens (from [@BotFather](https://t.me/BotFather))
- A MongoDB connection (Atlas free tier works fine, or your own MongoDB server) —
  one URL is enough, you just give each bot a different database name
- Your `APP_ID` and `API_HASH` from https://my.telegram.org

---

## 2. Connect to your VPS

```bash
ssh root@your_vps_ip
```

---

## 3. Install Docker and Docker Compose

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo systemctl enable docker
sudo systemctl start docker
```

Check it's installed correctly:

```bash
docker --version
docker compose version
```

(Optional) run Docker without sudo:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## 4. Upload the project to the VPS

From your **local machine**, upload the zip:

```bash
scp multi-file-sharing-10bots.zip root@your_vps_ip:/root/
```

Back on the **VPS**, unzip it:

```bash
cd /root
unzip multi-file-sharing-10bots.zip
cd muti-file-sharing-updated
```

(If `unzip` isn't installed: `sudo apt install -y unzip`)

---

## 5. Configure the `.env` file

Open it with a text editor:

```bash
nano .env
```

Fill in:

- **Shared section** (top of file) — `APP_ID`, `API_HASH`, `OWNER_ID`, `CHANNEL_ID`,
  `FORCE_SUB_CHANNEL_1-4`, `ADMINS`, messages, etc. Set once, applies to all 10 bots.
- **Per-bot section** — for each bot (`BOT1` through `BOT10`) fill in:
  - `BOTn_TOKEN` — the bot token from BotFather
  - `BOTn_DB_URL` — MongoDB connection string
  - `BOTn_DB_NAME` — database name (already pre-filled differently per bot, change if you like)
  - `BOTn_PORT` — already pre-set to 8081–8090, no change needed unless those ports are taken

Save and exit (in `nano`: `Ctrl+O`, `Enter`, then `Ctrl+X`).

---

## 6. Open firewall ports (if using UFW)

Each bot listens on its own port for health checks (8081–8090). If you use UFW:

```bash
sudo ufw allow 8081:8090/tcp
```

(This step is optional — these ports don't need to be public unless you want
to hit the health-check endpoint from outside. They're not required for the
bots to talk to Telegram.)

---

## 7. Build and start all 10 bots

Build the shared image once:

```bash
docker compose build bot1
```

Start all 10 bots in the background:

```bash
docker compose up -d
```

---

## 8. Verify everything is running

```bash
docker compose ps
```

You should see `filesharebot_1` through `filesharebot_10`, all "Up".

Check logs for a specific bot:

```bash
docker compose logs -f bot1
```

(`Ctrl+C` to stop watching logs — this won't stop the bot.)

Test each bot by messaging it `/start` on Telegram.

---

## 9. Common management commands

```bash
docker compose ps                   # status of all bots
docker compose logs -f bot5         # tail logs for one bot
docker compose restart bot3         # restart a single bot
docker compose stop                 # stop all bots (keeps containers)
docker compose down                 # stop & remove all containers
docker compose up -d                # start again after stop/down
docker compose up -d --build        # rebuild image after a code change, then restart all
```

---

## 10. Keeping bots running after reboot

The `docker-compose.yml` already sets `restart: unless-stopped` on every bot,
so they'll automatically restart if the VPS reboots or a bot crashes, as long
as Docker itself is enabled on boot (already handled in step 3 with
`systemctl enable docker`).

---

## 11. Updating the bots later

If you edit any code (e.g. `plugins/*.py`) and re-upload it to the VPS:

```bash
cd /root/muti-file-sharing-updated
docker compose up -d --build
```

This rebuilds the image and restarts all 10 bots with the new code, still
using the same `.env`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker: command not found` | Re-run step 3 |
| Bot doesn't respond on Telegram | Check `docker compose logs -f botN` for token/DB errors |
| `Bad Request: chat not found` for force-sub | Make sure the bot is an **admin** in the force-sub channels |
| Port already in use | Change `BOTn_PORT` in `.env` to a free port, then `docker compose up -d` |
| MongoDB connection errors | Double check `BOTn_DB_URL`, and that your VPS IP is whitelisted in MongoDB Atlas (Network Access) |

---

That's it — all 10 bots run independently, isolated in their own containers,
sharing one codebase and one `.env` file, each with its own token, port, and
MongoDB database.
