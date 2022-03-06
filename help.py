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

        embed.set_footer(text='Commands are all lowercase. This bot does not respond to DMs')

        embed.add_field(name="Getting Started",
            value='If you are a server admin, preferably create a readonly channel and say "@AiGoCode add {feature name}". If you are a server member, ask an admin which channel has the feature you are looking for',
            inline=False)

        embed.add_field(name="Features",
            value=" * singleplayer\n * display (recommended to have its own channel)",
            inline=False)

        embed.add_field(name='Command Usage Example',
            value='@AiGoCode add singleplayer\n@AiGoCode remove singleplayer',
            inline=False)

        embed.add_field(name="Supported Languages",
            value="1. Python 3.*\n2. Java 15.*",
            inline=False)

        await self.context.author.send(embed=embed)