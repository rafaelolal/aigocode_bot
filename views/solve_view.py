from typing import Dict, Any
import requests

import discord
from discord import Embed
from discord import Colour

class SolveView(discord.ui.View):
    def __init__(self, problem_menu_view, problem_id):
        super().__init__(timeout=None)
        self.problem_menu_view = problem_menu_view
        self.problem_id = problem_id

    @discord.ui.button(label='Submit', style=discord.ButtonStyle.green)
    async def submit(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]

        if interaction.message.author != msg.author and msg.attachments:
            file = msg.attachments[-1]
            embed = interaction.message.embeds[0]
            try:
                (await file.read()).decode('utf-8', 'strict')

            except UnicodeDecodeError:
                embed = self.response_embed(embed, 500)

            else:
                await interaction.response.defer()
                embed = self.response_embed(embed, 102)
                await interaction.message.edit(embed=embed)
                
                response = await self.run_file(file, str(interaction.user.id), self.problem_id)
                print(response)

                embed = self.response_embed(embed, 200, response['trace'])

                if embed.colour == Colour.green():
                    self.disable(interaction)

            await interaction.message.edit(embed=embed)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        embed = Embed(title="Bye bye!",
            colour=discord.Colour.red())
        embed.set_footer(text="closing in 5 seconds")

        await interaction.message.edit(embed=embed, delete_after=5, view=None)        
        self.stop()

    @staticmethod
    def response_embed(embed: Embed, status: int, trace: list[bool] = None) -> Embed:
        if status == 500:
            embed.description = 'There was an error reading your file. Try again'
            embed.colour = Colour.red()

        elif status == 102:
            embed.description = 'Running your program...'
            embed.colour = Colour.yellow()

        elif status == 200:
            desc = ''
            for test_case in enumerate(trace):
                case_results = []
                for case in test_case[1]['responses']:
                    if 'Traceback' in case['got']:
                        case_results.append('⚠️')
                        if test_case[1]['test case'] == 0 and case['case'] == 0:
                            desc = case['got']
                    
                    elif case['correct']:
                        case_results.insert(case['case'], '✅')
                            
                    elif not case['correct']:
                        case_results.insert(case['case'], '🛑')

                if not desc:
                    desc += ' '.join(case_results) + "\n"

            embed.description = desc

            if '⚠️' in desc or '🛑' in desc or 'Traceback' in desc:
                embed.colour = Colour.red()

            else:
                embed.colour = Colour.green()

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

        elif lang == 'java':
            json['ilanguage'] = 'java'
            json['iversion'] = '15.0.2'
            json['iextension'] = ''

        response = requests.post("https://codingcomp.netlify.app/api/bot/solve", json=json)
        return response.json()

    async def disable(self, interaction) -> None:
        for child in self.children:
            child.disabled = True

        self.stop()
        await interaction.message.edit(view=self)