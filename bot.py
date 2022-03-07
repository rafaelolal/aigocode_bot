import os
import sys
from pathlib import Path

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

from help_command import HelpCommand

bot = commands.Bot(command_prefix=commands.when_mentioned_or('|'), owner_id=250782339758555136,
                   intents=Intents.all(),
                   help_command=HelpCommand())

if __name__ == "__main__":
    cogs = {
    'cogs': ['helpers', 'events'],
    'cogs.db': ['db_management', 'mongodb'],
    'cogs.features': ['feature_manager'],
    'cogs.features.features': ['singleplayer', 'display', 'tictactoe'],}

    for dir in cogs:
        for cog in cogs[dir]:
            bot.load_extension(f"{dir}.{cog}")

    load_dotenv()
    bot.run(os.getenv('DISCORD_TOKEN'))