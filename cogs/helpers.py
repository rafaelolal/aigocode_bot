from logging import warning
from typing import Union

from discord.ext import commands
from discord import Message, NotFound
from discord.embeds import Embed
from discord.colour import Colour
class Helpers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_message(ctx, id: int) -> Union[Message, None]:
        try:
            return await ctx.fetch_message(id)
        
        except NotFound:
            pass

    def warning_embed(field_title, field_value):
        embed = Embed(title="Warning", 
            color=Colour.red())

        embed.set_footer(text="disappearing in 5 seconds")
        embed.add_field(name=field_title, value=field_value)

        return embed

def setup(bot):
    bot.add_cog(Helpers(bot))