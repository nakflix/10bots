# Deploying 10 bots (Docker Compose)

This package now runs **10 instances** of the same file-sharing bot, all built from
one Docker image, all configured from **one single `.env` file** (not a folder).

Every bot shares the exact same settings (force-sub channels, captions, messages,
admins, etc). The **only** things that differ per bot are:

- Bot token (`BOTn_TOKEN`)
- Port (`BOTn_PORT`)
- MongoDB URL (`BOTn_DB_URL`)
- MongoDB database name (`BOTn_DB_NAME`)

## 1. Edit `.env`

Open the `.env` file in the project root and fill in:

- The shared section at the top (APP_ID, API_HASH, OWNER_ID, CHANNEL_ID,
  FORCE_SUB_CHANNEL_1-4, ADMINS, messages, etc.) — set this once, it applies to
  all 10 bots.
- For **each** of the 10 bots, fill in `BOTn_TOKEN`, `BOTn_DB_URL`, and (optionally)
  change `BOTn_DB_NAME` / `BOTn_PORT` if you want different values. Ports already
  default to 8081–8090 so they don't clash on the same machine.

You can use one MongoDB cluster for all bots (just give each bot its own
`BOTn_DB_NAME` so their data doesn't mix), or separate clusters/URLs entirely —
both work since `BOTn_DB_URL` is set per bot.

## 2. Build the image (once)

```bash
docker compose build bot1
```

This builds a single image (`file-share-bot:latest`) used by all 10 services.

## 3. Start all 10 bots

```bash
docker compose up -d
```

This starts containers `filesharebot_1` through `filesharebot_10`, each running
its own bot token against its own Mongo database/port, all from the same code
and the same `.env` file.

## Useful commands

```bash
docker compose ps                 # see status of all 10 bots
docker compose logs -f bot5       # tail logs for one bot
docker compose restart bot3       # restart a single bot
docker compose down               # stop & remove all 10 bots
docker compose up -d --build      # rebuild image and restart everything
```

## Adding/removing bots

To run fewer than 10, just delete the corresponding `botN:` block in
`docker-compose.yml` (and its `BOTN_*` lines in `.env` if you like).
To add more than 10, copy a `botN:` block, bump the numbers, add the matching
`BOTN_TOKEN` / `BOTN_PORT` / `BOTN_DB_URL` / `BOTN_DB_NAME` lines to `.env`.

## Notes

- No code changes were needed — `config.py` already reads all values from
  environment variables, so the same codebase works for every bot; only the
  environment differs per container.
- Each bot runs in its own isolated container, so there's no session-file or
  log-file collision between bots even though they share the same image.
