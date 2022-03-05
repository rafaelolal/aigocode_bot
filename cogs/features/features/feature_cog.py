import discord
from discord.ext import commands

from cogs.helpers import Helpers
from cogs.db.db_management import DB

class Feature(commands.Cog):
    def __init__(self, bot, name, view):
        self.bot = bot
        self.name = name
        self.view = view

    async def add(self, ctx):
        DB.c.execute("SELECT * FROM guilds WHERE id=?",
            (ctx.guild.id,))
        guild = DB.c.fetchone()

        if guild[DB.channels.index(self.name)] != ', ':
            msg = await ctx.send('\u200b', view=self.view())
            DB.update_guild(ctx.guild.id,
                self.name, f"{ctx.channel.id}, {msg.id}")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This server already has this feature.")
            
            await ctx.send(embed=embed, delete_after=5)

    async def remove(self, ctx):
        channel_id, msg_id = DB.get_channel(ctx.guild.id, self.name)
        message = await Helpers.get_message(ctx, msg_id)
        if message:
            await message.delete()
            DB.update_guild(ctx.guild.id, self.name, ", ")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This feature is not present")
    
            await ctx.send(embed=embed, delete_after=5)