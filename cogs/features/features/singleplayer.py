import discord
from discord.ext import commands

from .feature_cog import Feature
from views.problem_menu_view import ProblemMenuView

class SingleplayerCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'singleplayer', SingleplayerView)

    @staticmethod
    async def add_singleplayer(ctx):
        await super().add_feature(ctx)

    @staticmethod
    async def remove_singleplayer(ctx):
        await super().remove_feature(ctx)

class SingleplayerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.playing_now = []

    async def interaction_check(self, interaction):
        if interaction.user in self.playing_now:
            await interaction.response.send_message("Finish solving the problem you already started or cancel it to start another", ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label='Play Singleplayer', style=discord.ButtonStyle.blurple, custom_id='play_singleplayer')
    async def play_singleplayer(self, button, interaction):
        self.playing_now.append(interaction.user)
        view = ProblemMenuView()
        await interaction.response.send_message(embed=view.response_embed(307),
            view=view,
            ephemeral=True)
    
        await view.wait()
        self.playing_now.remove(interaction.user)

def setup(bot):
    bot.add_cog(SingleplayerCommands(bot))