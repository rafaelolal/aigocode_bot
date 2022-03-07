from datetime import datetime
from discord.ext import commands
from discord import Embed, Colour, TextChannel

from cogs.features.features import (SingleplayerView,
    DisplayView,
    EditProjectView,
    TictactoeView,
    MazeView)

from cogs.db.db_management import DB

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(SingleplayerView())
        self.bot.add_view(DisplayView())
        self.bot.add_view(EditProjectView())
        self.bot.add_view(TictactoeView())
        self.bot.add_view(MazeView())
        print(f"Bot connected OK on {datetime.today()}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        guild = DB.fetch_one(payload.guild_id)
        if guild:
            for i, msg_info in enumerate(guild[:len(DB.channels)]):
                if str(payload.message_id) in msg_info:
                    DB.update_guild(payload.guild_id,
                        DB.channels[i], ', ')

                    break

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

        embed = Embed(title='AiGoCode Bot',
            url='https://www.aigocode.org/',
            description='Click the title to visit aigocode.org',
            colour=Colour.blue())

        embed.add_field(name="Getting Started",
            value='Hello, I am the AiGoCode Bot\n\nIf you are an admin, use "@AiGoCode help"')

        channels = await guild.fetch_channels()
        for channel in channels:
            if isinstance(channel, TextChannel):
                await channel.send(embed=embed)
                break

def setup(bot):
    bot.add_cog(Events(bot))