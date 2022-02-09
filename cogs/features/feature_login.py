import discord
from discord.ext import commands

from cogs.helpers import Helpers
from cogs.db.db_management import DB

class Feature(commands.Cog):
    def __init__(self, bot, name, view):
        self.bot = bot
        self.name = name
        self.view = view

    @commands.command()
    @commands.is_owner()
    async def add_feature(self, ctx):
        channel_id, message_id = DB.get_channel(ctx.guild.id,
            self.name)
        
        if not channel_id:
            msg = await ctx.send('\u200b', view=self.view())
            DB.update_guild(ctx.guild.id,
                self.name, f"{ctx.channel.id}, {msg.id}")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This channel already has this feature.")
            
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def remove_feature(self, ctx):
        channel_id, msg_id = DB.get_channel(ctx.guild.id, "stats")
        message = await Helpers.get_message(ctx, msg_id)
        if message:
            await message.delete()
            DB.update_guild(ctx.guild.id, self.name, ", ")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This feature is not present")
    
            await ctx.send(embed=embed, delete_after=5)

class LoginButton(discord.ui.Button):
    
    AUTH_API = ''

    def __init__(self, member_id):
        super().__init__(style=discord.ButtonStyle.green, label='Login', url=self.AUTH_API+str(member_id))

    async def callback(self, interaction):
        pass