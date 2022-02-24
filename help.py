from discord.ext import commands
from discord import Embed, Colour

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = Embed(title="AiGoCode Bot",
            url='https://www.aigocode.org/',
            description='Click on the title to visit aigocode.org',
            colour=Colour.blue())

        embed.set_footer(text='Commands are all lowercase and include underscores. This bot does not respond to DMs')

        embed.add_field(name="Getting Started",
            value='If you are a server admin, create a readonly channel and say "@AiGoCode Bot add_{feature name}"',
            inline=False)

        embed.add_field(name="Features",
            value=" * singleplayer",
            inline=False)

        embed.add_field(name='Command Usage Example',
            value='@AiGoCode Bot add_singleplayer\n@AiGoCode Bot remove_singleplayer',
            inline=False)

        embed.add_field(name="Supported Languages",
            value="1. Python 3.*\n2. Java 15.*",
            inline=False)

        await self.context.author.send(embed=embed)