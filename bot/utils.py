from discord.ext import commands
import random


class Utils(commands.Cog, name="Utilidades"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dado(self, ctx, number):
        if int(number) <= 0:
            await ctx.send("Põe um número acima de 0, burro")

        roll = random.randint(1, int(number))
        await ctx.send(f"🎲: {roll}")


def setup(bot):
    bot.add_cog(Utils(bot))
