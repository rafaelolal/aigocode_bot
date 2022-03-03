import os
import sys
from pathlib import Path

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

from help import CustomHelpCommand

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), owner_id=250782339758555136,
                   intents=Intents.all(),
                   help_command=CustomHelpCommand())

# path = Path(__file__).resolve().parent
# if str(path) not in sys.path:
#     sys.path.insert(1, str(path))

if __name__ == "__main__":
    cogs = {
    'cogs': ['helpers', 'events'],
    'cogs.db': ['db_management', 'mongodb'],
    'cogs.features': ['feature_manager'],
    'cogs.features.features': ['singleplayer'],}

    for dir in cogs:
        for cog in cogs[dir]:
            print(f"{dir}.{cog}")
            bot.load_extension(f"{dir}.{cog}")

    load_dotenv()
    bot.run(os.getenv('DISCORD_TOKEN'))