import discord
from discord.ext import commands

from cogs.helpers import Helpers
from cogs.db.db_management import DB
from .feature_login import Feature

class StatsCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'stats', StatsView)

class StatsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction):
        pass

    @discord.ui.button(label='See Stats', style=discord.ButtonStyle.blurple, custom_id='see_stats')
    async def see_stats(self, button, interaction):
        pass

    @staticmethod
    def create_embed():
        pass

def setup(bot):
    bot.add_cog(StatsCommands(bot))