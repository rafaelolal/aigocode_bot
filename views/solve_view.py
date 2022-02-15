from typing import Dict, Any
import requests

import discord
from discord import Embed
from discord import Colour

class SolveView(discord.ui.View):
    def __init__(self, problem_menu_view, problem_id):
        self.problem_menu_view = problem_menu_view
        self.problem_id = problem_id
        super().__init__(timeout=None)

    @discord.ui.button(label='Submit', style=discord.ButtonStyle.green)
    async def submit(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]
        if msg != interaction.message:
            if msg.attachments:
                file = msg.attachments[-1]
                embed = interaction.message.embeds[0]
                try:
                    (await file.read()).decode('utf-8', 'strict')

                except UnicodeDecodeError:
                    embed = SolveView.response_embed(embed, 500)

                else:
                    await interaction.response.defer()
                    embed = SolveView.response_embed(embed, 102)
                    await interaction.message.edit(embed=embed)
                    response = await SolveView.run_file(file, str(interaction.user.id), self.problem_id)
                    print(response)
                    if 'errorMessage' in response:
                        if 'Task timed out after' in response['errorMessage']:
                            embed = SolveView.response_embed(embed, 408)

                    elif response['correct'] == True:
                        if response['warn'] == True:
                            embed = SolveView.response_embed(embed, 208)
                        
                        else:
                            embed = SolveView.response_embed(embed, 200)

                        self.disable_children()

                await interaction.message.edit(embed=embed)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        # TODO REPEATED CODE code comes from helpers
        embed = Embed(title="Bye bye!",
            colour=discord.Colour.red())
        embed.set_footer(text="closing in 5 seconds")

        await interaction.message.edit(embed=embed, delete_after=5, view=None)
        self.stop()

    @staticmethod
    def response_embed(embed: Embed, status: int) -> Embed:
        if status == 500:
            embed.description = 'There was an error reading your file'
            embed.colour = Colour.red()

        elif status == 102:
            embed.description = 'Running your program...'
            embed.colour = Colour.yellow()

        elif status == 200:
            embed.description = "Correct!"
            embed.colour = Colour.green()

        elif status == 208:
            embed.description = "You have already solved this problem"
            embed.colour = Colour.dark_gold()

        elif status == 408:
            embed.description = "Your code is too slow!"
            embed.colour = Colour.red()

        return embed

    @staticmethod
    async def run_file(file: discord.Attachment, user_id: str, problem_id: str) -> Dict[str, Any]:
        content = (await file.read()).decode('utf-8', 'strict').replace('\r', '').replace('        ', '\t')
        lang = file.filename.split('.')[-1]
        json = {
            # TODO replace this with a env variable
            "key": '7e8e71c8-0308-4dcc-b09e-2b00dbec60c9',
            "icode": content,
            "idiscordid": user_id,
            "problemid": str(problem_id),
        }

        if lang == 'py':
            json['ilanguage'] = 'python3'
            json['iversion'] = '3.9.4'
            json['iextension'] = 'py'

        response = requests.post("https://codingcomp.netlify.app/api/bot/solve", json=json)
        return response.json()

    def disable_children(self) -> None:
        for child in self.children:
            child.disabled = True