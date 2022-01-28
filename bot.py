import os
import sys
from pathlib import Path

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), owner_id=250782339758555136,
                   intents=Intents.all(),)
                   # help_command=None)

path = Path(__file__).resolve().parent
if str(path) not in sys.path:
    sys.path.insert(1, str(path))

mongo_path = path / 'cogs'
if str(mongo_path) not in sys.path:
    sys.path.insert(1, str(mongo_path))

print(sys.path)

if __name__ == "__main__":
    for file in os.listdir(path / "cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

    for file in os.listdir(path / "db"):
        if file.endswith(".py"):
            bot.load_extension(f"db.{file[:-3]}")

    load_dotenv()
    bot.run(os.getenv('DISCORD_TOKEN'))