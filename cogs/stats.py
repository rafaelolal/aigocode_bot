import discord
from discord.ext import commands

from cogs.helpers import Helpers
from db.db_management import DB

class StatsCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def add_stats(self, ctx):
        channel_id, message_id = DB.get_channel(ctx.guild.id,
            'stats')
        
        if not channel_id:
            msg = await ctx.send('\u200b', view=StatsView())
            DB.update_guild(ctx.guild.id,
                "stats", f"{ctx.channel.id}, {msg.id}")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This channel already has this feature.")
            
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def remove_stats(self, ctx):
        channel_id, msg_id = DB.get_channel(ctx.guild.id, "stats")
        message = await Helpers.get_message(ctx, msg_id)
        if message:
            await message.delete()
            DB.update_guild(ctx.guild.id, "stats", ", ")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This feature is not present")
    
            await ctx.send(embed=embed, delete_after=5)

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