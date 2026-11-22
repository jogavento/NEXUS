# Security

- Keep `DISCORD_TOKEN` in `.env` or a secret manager; never commit it.
- If exposed, reset it immediately in the Discord Developer Portal.
- Use minimum bot permissions; NEXUS does not need Administrator.
- NEXUS does not request Message Content intent or scrape messages.
- Stored information is limited to explicit game participation: Discord IDs, game stats, inventory and cooldowns.
- Tell members what is stored and provide a process for data-removal requests.
- Report vulnerabilities privately to repository maintainers.
