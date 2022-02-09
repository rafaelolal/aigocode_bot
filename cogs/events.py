from textwrap import dedent
from datetime import datetime
import discord
from discord.channel import DMChannel
from discord.ext import commands

from cogs.features.singleplayer import SingleplayerView
from cogs.db.db_management import DB

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(SingleplayerView(self.bot))
        print(f"Bot connected OK on {datetime.today()}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == self.bot.user.name:
            return

        if isinstance(message.channel, DMChannel):
            await message.author.send(dedent("""
                Hello, I'm the AiGoCode bot!
                Visit our website for more information and practice.
                > *website link missing*
                
                **If you have any questions, contact a sesrver admin**
                *This bot does not respond to DMs*"""))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not DB.fetch_one(member.id):
            DB.add_member(member.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not DB.fetch_one(guild.id):
            DB.add_guild(guild.id)
            for member in guild.members:
                if not DB.fetch_one(member.id):
                    DB.add_member(member.id)

def setup(bot):
    bot.add_cog(Events(bot))