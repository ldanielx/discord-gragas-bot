from discord.ext import commands
from discord import Embed


class Manager(commands.Cog, name="Manager"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="reload",
        description="Reload BOT command",
    )
    @commands.is_owner()
    async def _reload(self, ctx, extension):
        try:
            self.bot.reload_extension(f"cogs.{extension}")
        except Exception as error:
            print(f"Error: {error}")

        embed = Embed(
            title="Reload",
            description=f"{extension} successfully reloaded",
            color=0xFF00C8,
        )
        await ctx.send(embed=embed)

    @commands.command(name="unload", description="Unload BOT command")
    @commands.is_owner()
    async def _unload(self, ctx, extension):
        try:
            self.bot.unload_extension(f"cogs.{extension}")
        except Exception as error:
            print(f"Error: {error}")

        embed = Embed(
            title="Unload",
            description=f"{extension} successfully unloaded",
            color=0xFF0000,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="quit",
        description="Kill Gragas BOT",
    )
    @commands.is_owner()
    async def _quit(self, ctx, extension):
        await self.bot.close()


def setup(bot):
    bot.add_cog(Manager(bot))
