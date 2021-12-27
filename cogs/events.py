from textwrap import dedent

import discord
from discord.channel import DMChannel
from discord.ext import commands
from singleplayer import PlaySingleplayer

from db.db_management import DB

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == self.bot.user.name:
            return

        if isinstance(message.channel, DMChannel):
            await message.author.send(dedent("""
                Hello, I'm the AiGoCode bot!
                Visit our website for more information and practice.
                > *website link missing*
                
                **If you have any questions, contact a Manager**
                *This bot does not respond to DMs*"""))

    @staticmethod
    @commands.Cog.listener()
    # TODO remove member from database
    async def on_member_remove(member):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(PlaySingleplayer(self.bot))

def setup(bot):
    bot.add_cog(Events(bot))