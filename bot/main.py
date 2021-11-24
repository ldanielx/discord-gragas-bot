import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

load_dotenv()

bot_prefix = os.getenv("bot_prefix")
token = os.getenv("token")

bot = commands.Bot(command_bot_prefix=bot_prefix, case_insensitive=True)


@bot.event
async def on_ready():
    print(
        f"\n---------------------------------------------------\n"
        f"Bot Ready!\n"
        f"Current bot_prefix: {bot_prefix}\n"
        f"---------------------------------------------------"
    )
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, n="")
    )


@bot.command()
async def dado(ctx, number):
    if int(number) <= 0:
        await ctx.send("Põe um número acima de 0, burro")

    roll = random.randint(1, int(number))
    await ctx.send(f"O número que saiu no dado foi: {roll}")


bot.run(token)
