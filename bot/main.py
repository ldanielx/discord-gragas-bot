import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot_prefix = os.getenv("bot_prefix")
bot_token = os.getenv("token")
bot_intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=bot_prefix,
    case_insensitive=True,
    status=discord.Status.idle,
    intents=bot_intents,
    activity=discord.Game(
        type=discord.ActivityType.watching,
        name="DVD do lc",
    ),
)

bot.load_extension("cogs.manager")
bot.load_extension("cogs.utils")
bot.load_extension("cogs.music")


@bot.event
async def on_ready():
    print(
        f"\n---------------------------------------------------\n"
        f"Bot Ready!\n"
        f"Current bot_prefix: {bot_prefix}\n"
        f"---------------------------------------------------"
    )


bot.run(bot_token)
