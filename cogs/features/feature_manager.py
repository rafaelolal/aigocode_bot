import discord
from discord.ext import commands

from cogs.helpers import Helpers
from cogs.db.db_management import DB
from features import *

class FeatureManager(commands.Cog):
    features = ['singleplayer', 'display']
    add_feature = {name: eval(f'{name.capitalize()}.add_{name}') for name in features}
    remove_feature = {name: eval(f'{name.capitalize()}.remove_{name}') for name in features}

    def __init__(self, bot, name, view):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, feature):
        self.add_feature[feature](ctx)

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, feature):
        self.remove_feature[feature](ctx)