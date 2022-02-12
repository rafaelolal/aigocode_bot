from math import ceil
from typing import Any, Dict, List
import requests

import discord
from discord.ext import commands

from cogs.helpers import Helpers
from cogs.db.db_management import DB
from .feature_cog import Feature
from .views.problem_menu_view import ProblemMenuView

class SingleplayerCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'singleplayer', SingleplayerView)

    @commands.command()
    async def add_singleplayer(self, ctx):
        await super().add_feature(ctx)

    @commands.command()
    async def remove_singleplayer(self, ctx):
        await super().remove_feature(ctx)

class SingleplayerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.playing_now = []

    async def interaction_check(self, interaction):
        return interaction.user not in self.playing_now

    @discord.ui.button(label='Play Singleplayer', style=discord.ButtonStyle.blurple, custom_id='play_singleplayer')
    async def play_singleplayer(self, button, interaction):
        self.playing_now.append(interaction.user)
        view = ProblemMenuView()
        await interaction.response.send_message(embed=view.create_embed(0),
            view=view,
            ephemeral=True)
    
        await view.wait()
        self.playing_now.remove(interaction.user)

def setup(bot):
    bot.add_cog(SingleplayerCommands(bot))