import discord
from discord import app_commands
from discord.ext import commands
from ..constants import EMOJI, LABEL, STRUCTURES, QUESTS
from ..repositories import Repository

class WorldCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = Repository(bot.database.conn)

    async def active_world(self, interaction):
        if interaction.guild is None:
            await interaction.response.send_message("NEXUS runs inside a server, not DMs.",ephemeral=True)
            return None
        world = await self.repo.world(interaction.guild.id)
        if not world:
            await interaction.response.send_message("Ask an admin to run `/world_create` first.",ephemeral=True)
            return None
        if not world["active"]:
            await interaction.response.send_message("This civilization is paused.",ephemeral=True)
            return None
        return world

    @app_commands.command(name="nexus",description="Open the NEXUS civilization home panel.")
    async def nexus(self, interaction: discord.Interaction):
        w = await self.active_world(interaction)
        if not w: return
        treasury = await self.repo.treasury(interaction.guild.id)
        e = discord.Embed(title=f"🌌 {w['name']} — Living Civilization",
            description="A shared world shaped by every citizen. Gather, explore and build together.",
            color=discord.Color.blurple())
        e.add_field(name="Civilization",value=f"Level **{w['level']}** · {w['xp']} XP",inline=True)
        e.add_field(name="Treasury",value="\n".join(
            f"{EMOJI[r]} {LABEL[r]}: **{treasury.get(r,0)}**" for r in EMOJI),inline=True)
        e.add_field(name="Start here",value="`/gather` · `/explore` · `/profile` · `/quests`",inline=False)
        e.set_footer(text="NEXUS • Your community, your civilization")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="world",description="View civilization status, treasury and structures.")
    async def world(self, interaction: discord.Interaction):
        w = await self.active_world(interaction)
        if not w: return
        gid = interaction.guild.id
        treasury, structures = await self.repo.treasury(gid), await self.repo.structures(gid)
        e = discord.Embed(title=f"🌍 {w['name']} — World Status",color=discord.Color.teal())
        e.add_field(name="Level",value=f"**{w['level']}** · {w['xp']} XP",inline=True)
        e.add_field(name="Treasury",value="\n".join(
            f"{EMOJI[r]} {LABEL[r]}: **{treasury.get(r,0)}**" for r in EMOJI),inline=False)
        e.add_field(name="Structures",value="\n".join(
            f"🏛️ {v['name']}: Level **{structures.get(k,0)}**" for k,v in STRUCTURES.items()),inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="quests",description="View today's shared community quests.")
    async def quests(self, interaction: discord.Interaction):
        w = await self.active_world(interaction)
        if not w: return
        progress = await self.repo.quests(interaction.guild.id)
        lines = []
        for q in QUESTS:
            p = progress[q["key"]]
            mark = "✅" if p["completed"] else "🔹"
            lines.append(f"{mark} **{q['title']}** — {q['description']}\n`{p['progress']}/{q['target']}` · Reward: {q['xp']} world XP")
        e = discord.Embed(title="📜 Community Quests",description="\n\n".join(lines),color=discord.Color.gold())
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="leaderboard",description="Show the top civilization contributors.")
    async def leaderboard(self, interaction: discord.Interaction):
        w = await self.active_world(interaction)
        if not w: return
        rows = await self.repo.leaderboard(interaction.guild.id)
        if not rows:
            await interaction.response.send_message("No citizens yet. Start with `/gather`!")
            return
        lines = []
        medals = ["🥇","🥈","🥉"]
        for i,row in enumerate(rows):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"Citizen {str(row['user_id'])[-4:]}"
            lines.append(f"{medals[i] if i<3 else f'#{i+1}'} **{discord.utils.escape_markdown(name)}** — Level {row['level']} · {row['xp']} XP")
        await interaction.response.send_message(embed=discord.Embed(title="🏆 Hall of Contributors",description="\n".join(lines),color=discord.Color.gold()))

async def setup(bot):
    await bot.add_cog(WorldCog(bot))
