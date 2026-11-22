# NEXUS — A Living Civilization for Discord

A persistent, cooperative civilization simulator. Members gather resources, explore a frontier, donate to a shared treasury, construct buildings, complete daily community quests and climb a contributor leaderboard.

## Features
- Slash-command interface (`discord.py` 2.x); no Message Content intent.
- One persistent world per Discord server.
- Personal citizen profiles, XP, levels and resource inventories.
- Shared treasury and upgradeable structures.
- Gathering/exploration cooldowns and daily community quests.
- Admin setup/pause/rename controls.
- SQLite persistence, Docker deployment, tests and contribution templates.
- Privacy-conscious: stores game actions only; does not read chat history.

## Commands
`/nexus` home · `/world` status · `/profile` citizen profile · `/gather` collect · `/explore` expedition · `/donate` treasury contribution · `/build` upgrade a structure · `/quests` daily objectives · `/leaderboard` top citizens · `/world_create` admin setup · `/world_settings` admin controls.

## Local setup
1. Create an application and bot at https://discord.com/developers/applications.
2. Invite with OAuth2 scopes `bot` and `applications.commands`. Grant only basic view/send/embed permissions; do not grant Administrator.
3. Copy `.env.example` to `.env`, add your token, then:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m nexus
```

On Windows activate with `.venv\\Scripts\\Activate.ps1`.

Set `DEV_GUILD_ID` in `.env` to sync commands instantly to a private test server. Remove it for global sync.

## Docker
```sh
cp .env.example .env
# Edit .env and set DISCORD_TOKEN
docker compose up -d --build
docker compose logs -f
```

## GitHub publishing
Create an empty GitHub repository, then from this project directory:
```sh
git init
git add .
git commit -m "feat: initial NEXUS civilization bot"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nexus-discord-bot.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Never commit `.env`, tokens, or database files.

## Android / Alpine
```sh
apk update
apk add python3 py3-pip py3-virtualenv git
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m nexus
```
For reliable 24/7 uptime, use a VPS or Docker host rather than an Android terminal session.

## Configuration
See `.env.example`. SQLite is suitable for a single bot process and small communities. For larger scale, migrate to PostgreSQL and distributed locking.

## Contributing
See `CONTRIBUTING.md`. Run `pytest` and `ruff check .` before submitting changes.

## Beta scope
This is a functional v0.1 starter release, not a fully load-tested production SaaS. Test in a private server, review permissions, back up `data/nexus.db`, and inspect logs before inviting a large community.
