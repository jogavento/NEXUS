# Architecture

```text
Discord slash command
        |
        v
  discord.py Cogs       (interaction and presentation)
        |
        v
   GameService          (gameplay rules and rewards)
        |
        v
   Repository           (SQL queries and transactions)
        |
        v
   SQLite database      (persistent server world)
```

Tables: `worlds`, `citizens`, `inventory`, `treasury`, `structures`, `cooldowns`, `quest_progress`.

The v0.1 release is single-process SQLite. Do not run multiple bot replicas against the same SQLite file. For larger communities, migrate to PostgreSQL and add distributed cooldown/locking.
