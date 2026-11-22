import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    token: str
    dev_guild_id: int | None
    database_path: str
    gather_cooldown: int
    explore_cooldown: int
    log_level: str

    @classmethod
    def load(cls):
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token or token == "put_your_bot_token_here":
            raise RuntimeError("Set DISCORD_TOKEN in your .env file.")
        guild = os.getenv("DEV_GUILD_ID", "").strip()
        return cls(
            token, int(guild) if guild else None,
            os.getenv("DATABASE_PATH", "data/nexus.db"),
            max(5, int(os.getenv("GATHER_COOLDOWN_SECONDS", "60"))),
            max(10, int(os.getenv("EXPLORE_COOLDOWN_SECONDS", "120"))),
            os.getenv("LOG_LEVEL", "INFO").upper(),
        )

    def prepare(self):
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
