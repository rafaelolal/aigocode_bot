from textwrap import dedent

import discord
from discord.embeds import Embed
from discord.ext import commands
from discord.utils import get

class PlaySingleplayer(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.playing_now = []

    async def interaction_check(self, interaction):
        pass

    @discord.ui.button(label='Play Singeplayer', style=discord.ButtonStyle.blurple, custom_id='play_singleplayer')
    async def play_singleplayer(self, button, interaction):
        await interaction.response.defer()
        await interaction.user.send('Get pen and paper, open up your text editor, and get great to debug! Press the button whenever you are ready.', view=Submission())

class Submission(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)

    @discord.ui.button(label='Begin', style=discord.ButtonStyle.green)
    async def play_singleplayer(self, button, interaction):
        await interaction.response.defer()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def play_singleplayer(self, button, interaction):
        interaction.response.edit_message(content="*You canceled this game. This message will be deleted in 10 seconds.*", view=None, delete_after=10)

class SingleplayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def update_singleplayer_button(self, ctx):
        await ctx.send('\u200b', view=PlaySingleplayer(self.bot))

def setup(bot):
    bot.add_cog(SingleplayerCommands(bot))