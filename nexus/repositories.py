from datetime import date
import time
from .constants import RESOURCES, QUESTS

class Repository:
    def __init__(self, db):
        self.db = db

    async def world(self, gid):
        cur = await self.db.execute("SELECT * FROM worlds WHERE guild_id=?", (gid,))
        return await cur.fetchone()

    async def create_world(self, gid, name):
        await self.db.execute("INSERT OR IGNORE INTO worlds(guild_id,name) VALUES(?,?)", (gid, name[:60]))
        for r in RESOURCES:
            await self.db.execute("INSERT OR IGNORE INTO treasury(guild_id,resource) VALUES(?,?)", (gid,r))
        await self.db.commit()
        return await self.world(gid)

    async def set_world(self, gid, name=None, active=None):
        if name is not None:
            await self.db.execute("UPDATE worlds SET name=? WHERE guild_id=?", (name[:60],gid))
        if active is not None:
            await self.db.execute("UPDATE worlds SET active=? WHERE guild_id=?", (int(active),gid))
        await self.db.commit()

    async def ensure_citizen(self, gid, uid):
        await self.db.execute("INSERT OR IGNORE INTO citizens(guild_id,user_id) VALUES(?,?)",(gid,uid))
        for r in RESOURCES:
            await self.db.execute(
                "INSERT OR IGNORE INTO inventory(guild_id,user_id,resource) VALUES(?,?,?)",(gid,uid,r))
        await self.db.commit()

    async def profile(self, gid, uid):
        await self.ensure_citizen(gid,uid)
        cur = await self.db.execute("SELECT * FROM citizens WHERE guild_id=? AND user_id=?",(gid,uid))
        citizen = await cur.fetchone()
        cur = await self.db.execute("SELECT resource,amount FROM inventory WHERE guild_id=? AND user_id=?",(gid,uid))
        return citizen, {r["resource"]:r["amount"] for r in await cur.fetchall()}

    async def add_resource(self, gid, uid, resource, amount):
        await self.ensure_citizen(gid,uid)
        await self.db.execute(
            "UPDATE inventory SET amount=amount+? WHERE guild_id=? AND user_id=? AND resource=?",
            (amount,gid,uid,resource))
        await self.db.commit()

    async def award_xp(self, gid, uid, amount):
        await self.ensure_citizen(gid,uid)
        cur = await self.db.execute("SELECT xp,level FROM citizens WHERE guild_id=? AND user_id=?",(gid,uid))
        row = await cur.fetchone()
        xp, level = row["xp"] + amount, row["level"]
        while xp >= level * 100:
            xp -= level * 100
            level += 1
        await self.db.execute(
            "UPDATE citizens SET xp=?,level=?,contributions=contributions+1 WHERE guild_id=? AND user_id=?",
            (xp,level,gid,uid))
        await self.db.commit()

    async def cooldown(self, gid, uid, action, seconds):
        now = time.time()
        cur = await self.db.execute(
            "SELECT ready_at FROM cooldowns WHERE guild_id=? AND user_id=? AND action=?",
            (gid,uid,action))
        row = await cur.fetchone()
        if row and row["ready_at"] > now:
            return int(row["ready_at"] - now) + 1
        await self.db.execute(
            """INSERT INTO cooldowns(guild_id,user_id,action,ready_at) VALUES(?,?,?,?)
               ON CONFLICT(guild_id,user_id,action) DO UPDATE SET ready_at=excluded.ready_at""",
            (gid,uid,action,now+seconds))
        await self.db.commit()
        return 0

    async def add_world_xp(self, gid, amount):
        cur = await self.db.execute("SELECT xp,level FROM worlds WHERE guild_id=?",(gid,))
        row = await cur.fetchone()
        if not row:
            return
        xp, level = row["xp"] + amount, row["level"]
        while xp >= level * 500:
            xp -= level * 500
            level += 1
        await self.db.execute("UPDATE worlds SET xp=?,level=? WHERE guild_id=?",(xp,level,gid))
        await self.db.commit()

    async def treasury(self, gid):
        cur = await self.db.execute("SELECT resource,amount FROM treasury WHERE guild_id=?",(gid,))
        return {r["resource"]:r["amount"] for r in await cur.fetchall()}

    async def donate(self, gid, uid, resource, amount):
        await self.ensure_citizen(gid,uid)
        await self.db.execute("BEGIN IMMEDIATE")
        try:
            cur = await self.db.execute(
                "SELECT amount FROM inventory WHERE guild_id=? AND user_id=? AND resource=?",
                (gid,uid,resource))
            row = await cur.fetchone()
            if not row or row["amount"] < amount:
                await self.db.rollback()
                return False
            await self.db.execute(
                "UPDATE inventory SET amount=amount-? WHERE guild_id=? AND user_id=? AND resource=?",
                (amount,gid,uid,resource))
            await self.db.execute(
                """INSERT INTO treasury(guild_id,resource,amount) VALUES(?,?,?)
                   ON CONFLICT(guild_id,resource) DO UPDATE SET amount=amount+excluded.amount""",
                (gid,resource,amount))
            await self.db.commit()
            await self.award_xp(gid,uid,max(1,amount))
            await self.add_world_xp(gid,amount)
            if resource in ("wood","stone"):
                await self.quest_progress(gid,resource,amount)
            return True
        except Exception:
            await self.db.rollback()
            raise

    async def build(self, gid, key, cost):
        await self.db.execute("BEGIN IMMEDIATE")
        try:
            for resource, amount in cost.items():
                cur = await self.db.execute(
                    "SELECT amount FROM treasury WHERE guild_id=? AND resource=?",(gid,resource))
                row = await cur.fetchone()
                if not row or row["amount"] < amount:
                    await self.db.rollback()
                    return False
            for resource, amount in cost.items():
                await self.db.execute(
                    "UPDATE treasury SET amount=amount-? WHERE guild_id=? AND resource=?",
                    (amount,gid,resource))
            await self.db.execute(
                """INSERT INTO structures(guild_id,key,level) VALUES(?,?,1)
                   ON CONFLICT(guild_id,key) DO UPDATE SET level=level+1""",(gid,key))
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            raise

    async def structures(self, gid):
        cur = await self.db.execute("SELECT key,level FROM structures WHERE guild_id=?",(gid,))
        return {r["key"]:r["level"] for r in await cur.fetchall()}

    async def quest_progress(self, gid, key, amount):
        today = date.today().isoformat()
        definition = next((q for q in QUESTS if q["key"] == key),None)
        if not definition:
            return
        await self.db.execute(
            "INSERT OR IGNORE INTO quest_progress(guild_id,quest_key,day) VALUES(?,?,?)",
            (gid,key,today))
        cur = await self.db.execute(
            "SELECT progress,completed FROM quest_progress WHERE guild_id=? AND quest_key=? AND day=?",
            (gid,key,today))
        row = await cur.fetchone()
        if row["completed"]:
            return
        progress = min(definition["target"],row["progress"]+amount)
        done = progress >= definition["target"]
        await self.db.execute(
            "UPDATE quest_progress SET progress=?,completed=? WHERE guild_id=? AND quest_key=? AND day=?",
            (progress,int(done),gid,key,today))
        if done:
            await self.add_world_xp(gid,definition["xp"])
        await self.db.commit()

    async def quests(self, gid):
        today = date.today().isoformat()
        result = {}
        for q in QUESTS:
            await self.db.execute(
                "INSERT OR IGNORE INTO quest_progress(guild_id,quest_key,day) VALUES(?,?,?)",
                (gid,q["key"],today))
            cur = await self.db.execute(
                "SELECT progress,completed FROM quest_progress WHERE guild_id=? AND quest_key=? AND day=?",
                (gid,q["key"],today))
            result[q["key"]] = dict(await cur.fetchone())
        await self.db.commit()
        return result

    async def leaderboard(self, gid):
        cur = await self.db.execute(
            "SELECT user_id,xp,level,contributions FROM citizens WHERE guild_id=? ORDER BY level DESC,xp DESC LIMIT 10",
            (gid,))
        return await cur.fetchall()
