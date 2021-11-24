import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

load_dotenv()

prefix = os.getenv("prefix")
token = os.getenv("token")

client = commands.Bot(command_prefix=prefix, case_insensitive=True)


@client.event
async def on_ready():
    print(
        f"\n---------------------------------------------------\n"
        f"Bot Ready!\n"
        f"Current Prefix: {prefix}\n"
        f"---------------------------------------------------"
    )
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, n="")
    )


@client.command()
async def dado(ctx, number):
    if int(number) <= 0:
        await ctx.send("Põe um número acima de 0, burro")

    roll = random.randint(1, int(number))
    await ctx.send(f"O número que saiu no dado foi: {roll}")


client.run(token)
