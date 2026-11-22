import discord
from discord import app_commands
from discord.ext import commands
from ..constants import EMOJI, LABEL, STRUCTURES
from ..repositories import Repository
from ..services import GameService

class CitizenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = Repository(bot.database.conn)
        self.game = GameService(self.repo)

    async def check_world(self, interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Use NEXUS inside a server.",ephemeral=True)
            return False
        w = await self.repo.world(interaction.guild.id)
        if not w:
            await interaction.response.send_message("Ask an admin to create the world with `/world_create`.",ephemeral=True)
            return False
        if not w["active"]:
            await interaction.response.send_message("This world is paused.",ephemeral=True)
            return False
        return True

    @app_commands.command(name="profile",description="View your citizen profile and inventory.")
    async def profile(self, interaction: discord.Interaction):
        if not await self.check_world(interaction): return
        c, inv = await self.repo.profile(interaction.guild.id,interaction.user.id)
        e = discord.Embed(title=f"🧑‍🚀 {interaction.user.display_name} — Citizen",color=discord.Color.blurple())
        e.add_field(name="Progress",value=f"Level **{c['level']}** · {c['xp']} XP",inline=True)
        e.add_field(name="Contributions",value=f"**{c['contributions']}**",inline=True)
        e.add_field(name="Inventory",value="\n".join(f"{EMOJI[r]} {LABEL[r]}: **{inv[r]}**" for r in EMOJI),inline=False)
        await interaction.response.send_message(embed=e,ephemeral=True)

    @app_commands.command(name="gather",description="Gather a random resource for your inventory.")
    async def gather(self, interaction: discord.Interaction):
        if not await self.check_world(interaction): return
        r = await self.game.gather(interaction.guild.id,interaction.user.id,self.bot.settings.gather_cooldown)
        if "wait" in r:
            await interaction.response.send_message(f"⏳ Try again in **{r['wait']} seconds**.",ephemeral=True); return
        await interaction.response.send_message(f"{EMOJI[r['resource']]} You gathered **{r['amount']} {LABEL[r['resource']]}** and earned **12 XP**. Use `/donate` to help the shared treasury.")

    @app_commands.command(name="explore",description="Explore the frontier for resources and discoveries.")
    async def explore(self, interaction: discord.Interaction):
        if not await self.check_world(interaction): return
        r = await self.game.explore(interaction.guild.id,interaction.user.id,self.bot.settings.explore_cooldown)
        if "wait" in r:
            await interaction.response.send_message(f"Wait **{r['wait']} seconds** before your next expedition.",ephemeral=True); return
        found = f"\nFound: **{r['amount']} {LABEL[r['resource']]}**" if r["resource"] else ""
        e = discord.Embed(title="🧭 Expedition Report",description=r["story"]+found,color=discord.Color.green())
        e.add_field(name="Experience",value=f"+{r['xp']} XP")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="donate",description="Donate resources from your inventory to the shared treasury.")
    @app_commands.choices(resource=[
        app_commands.Choice(name="Wood",value="wood"),app_commands.Choice(name="Stone",value="stone"),
        app_commands.Choice(name="Crystal",value="crystal"),app_commands.Choice(name="Food",value="food")])
    async def donate(self, interaction: discord.Interaction, resource: app_commands.Choice[str],
                     amount: app_commands.Range[int,1,500]):
        if not await self.check_world(interaction): return
        ok = await self.repo.donate(interaction.guild.id,interaction.user.id,resource.value,amount)
        if not ok:
            await interaction.response.send_message("You don't have enough of that resource.",ephemeral=True); return
        await interaction.response.send_message(f"🤝 You contributed **{amount} {LABEL[resource.value]}** to the civilization treasury. Thank you!")

    @app_commands.command(name="build",description="Spend shared treasury resources to upgrade a structure.")
    @app_commands.choices(structure=[
        app_commands.Choice(name="Frontier Outpost",value="outpost"),
        app_commands.Choice(name="Grand Library",value="library"),
        app_commands.Choice(name="Sky Greenhouse",value="greenhouse")])
    async def build(self, interaction: discord.Interaction, structure: app_commands.Choice[str]):
        if not await self.check_world(interaction): return
        definition = STRUCTURES[structure.value]
        ok = await self.repo.build(interaction.guild.id,structure.value,definition["cost"])
        if not ok:
            t = await self.repo.treasury(interaction.guild.id)
            missing = ", ".join(f"{LABEL[r]}: need {n-t.get(r,0)} more" for r,n in definition["cost"].items() if t.get(r,0)<n)
            await interaction.response.send_message(f"The treasury needs more resources: {missing}.",ephemeral=True); return
        await self.repo.award_xp(interaction.guild.id,interaction.user.id,35)
        await self.repo.add_world_xp(interaction.guild.id,definition["xp"])
        cost = ", ".join(f"{n} {LABEL[r]}" for r,n in definition["cost"].items())
        await interaction.response.send_message(f"🏗️ **{definition['name']}** upgraded! {definition['description']}\nResources used: {cost}\nYou earned **35 XP**.")

async def setup(bot):
    await bot.add_cog(CitizenCog(bot))
