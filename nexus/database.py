from pathlib import Path
import aiosqlite

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS worlds (
 guild_id INTEGER PRIMARY KEY, name TEXT NOT NULL DEFAULT 'NEXUS',
 level INTEGER NOT NULL DEFAULT 1, xp INTEGER NOT NULL DEFAULT 0,
 active INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS citizens (
 guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL, xp INTEGER NOT NULL DEFAULT 0,
 level INTEGER NOT NULL DEFAULT 1, contributions INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(guild_id,user_id), FOREIGN KEY(guild_id) REFERENCES worlds(guild_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS inventory (
 guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL, resource TEXT NOT NULL,
 amount INTEGER NOT NULL DEFAULT 0 CHECK(amount >= 0), PRIMARY KEY(guild_id,user_id,resource),
 FOREIGN KEY(guild_id,user_id) REFERENCES citizens(guild_id,user_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS treasury (
 guild_id INTEGER NOT NULL, resource TEXT NOT NULL, amount INTEGER NOT NULL DEFAULT 0 CHECK(amount >= 0),
 PRIMARY KEY(guild_id,resource), FOREIGN KEY(guild_id) REFERENCES worlds(guild_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS structures (
 guild_id INTEGER NOT NULL, key TEXT NOT NULL, level INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(guild_id,key), FOREIGN KEY(guild_id) REFERENCES worlds(guild_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS cooldowns (
 guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL, action TEXT NOT NULL, ready_at REAL NOT NULL,
 PRIMARY KEY(guild_id,user_id,action)
);
CREATE TABLE IF NOT EXISTS quest_progress (
 guild_id INTEGER NOT NULL, quest_key TEXT NOT NULL, day TEXT NOT NULL,
 progress INTEGER NOT NULL DEFAULT 0, completed INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(guild_id,quest_key,day), FOREIGN KEY(guild_id) REFERENCES worlds(guild_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_citizens_rank ON citizens(guild_id,xp DESC);
"""

class Database:
    def __init__(self, path):
        self.path = path
        self.conn = None

    async def connect(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None
