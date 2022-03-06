import discord
from discord.ext import commands

from ..helpers import Helpers
from ..db.db_management import DB
from .features import SingleplayerCommands, DisplayCommands

class FeatureManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.features = ['singleplayer', 'display']
        self.cogs = bot.cogs

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, feature):
        await self.cogs[f'{feature.capitalize()}Commands'].add(ctx)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, feature):
        await self.cogs[f'{feature.capitalize()}Commands'].remove(ctx)

def setup(bot):
    bot.add_cog(FeatureManager(bot))