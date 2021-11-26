import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

bot_prefix = os.getenv("bot_prefix")
token = os.getenv("token")

bot = commands.Bot(command_prefix=bot_prefix, case_insensitive=True)
bot.load_extension("music")
bot.load_extension("utils")


@bot.event
async def on_ready():
    print(
        f"\n---------------------------------------------------\n"
        f"Bot Ready!\n"
        f"Current bot_prefix: {bot_prefix}\n"
        f"---------------------------------------------------"
    )
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            n="https://www.youtube.com/watch?v=UMfpkBRH3ro",
        )
    )


bot.run(token)
