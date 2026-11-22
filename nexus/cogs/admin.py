import discord
from discord import app_commands
from discord.ext import commands
from ..repositories import Repository

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.repo = Repository(bot.database.conn)

    @app_commands.command(name="world_create",description="Create this server's NEXUS civilization.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def world_create(self, interaction: discord.Interaction, name: app_commands.Range[str,2,60]="NEXUS"):
        if interaction.guild is None:
            await interaction.response.send_message("Server only.",ephemeral=True); return
        existing = await self.repo.world(interaction.guild.id)
        await self.repo.create_world(interaction.guild.id,name)
        msg = f"🌌 **{name}** is ready! Citizens can use `/nexus`, `/gather` and `/explore`."
        if existing: msg = f"World already exists. Existing progress was preserved; current name: **{existing['name']}**."
        await interaction.response.send_message(msg)

    @app_commands.command(name="world_settings",description="Rename or pause/resume this server's world.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def world_settings(self, interaction: discord.Interaction,
                             name: app_commands.Range[str,2,60] | None=None,
                             active: bool | None=None):
        if interaction.guild is None:
            await interaction.response.send_message("Server only.",ephemeral=True); return
        w = await self.repo.world(interaction.guild.id)
        if not w:
            await interaction.response.send_message("Run `/world_create` first.",ephemeral=True); return
        if name is None and active is None:
            await interaction.response.send_message("Set a new name or choose active true/false.",ephemeral=True); return
        await self.repo.set_world(interaction.guild.id,name,active)
        changes = ([f"name → **{name}**"] if name else []) + (["world resumed" if active else "world paused"] if active is not None else [])
        await interaction.response.send_message("Updated: "+", ".join(changes))

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
