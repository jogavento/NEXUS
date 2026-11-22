import logging
import discord
from discord.ext import commands
from .database import Database

log = logging.getLogger(__name__)

class NexusBot(commands.Bot):
    def __init__(self, settings):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        self.settings = settings
        self.database = Database(settings.database_path)

    async def setup_hook(self):
        await self.database.connect()
        for ext in ("nexus.cogs.world", "nexus.cogs.citizen", "nexus.cogs.admin"):
            await self.load_extension(ext)
        if self.settings.dev_guild_id:
            guild = discord.Object(id=self.settings.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %s commands to dev guild %s",len(synced),guild.id)
        else:
            synced = await self.tree.sync()
            log.info("Synced %s global commands",len(synced))

    async def on_ready(self):
        log.info("NEXUS online: %s",self.user)

    async def close(self):
        await self.database.close()
        await super().close()
