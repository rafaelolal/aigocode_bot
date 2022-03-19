from typing import Dict, Any
import requests

import discord
from discord import Embed
from discord import Colour

class ProblemView(discord.ui.View):
    
    langs = ['py', 'java']

    def __init__(self, problem_menu_view, problem_id):
        super().__init__(timeout=None)
        self.problem_menu_view = problem_menu_view
        self.problem_id = problem_id

    @discord.ui.button(label='Submit', style=discord.ButtonStyle.green)
    async def submit(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]

        if interaction.message.author != msg.author and msg.attachments:
            embed = interaction.message.embeds[0]

            file = msg.attachments[-1]
            file_info = await ProblemView.read(file)
            if file_info:
                await interaction.response.defer()
                embed = self.response_embed(embed, 102)
                await interaction.message.edit(embed=embed)
                
                response = self.run_file(file_info, interaction.user.id, self.problem_id)
                print(response)

                embed = self.response_embed(embed, 200, response)

                if embed.colour == Colour.green():
                    await self.disable_submission(interaction)

            else:
                embed = self.response_embed(embed, 500)

            await interaction.message.edit(embed=embed)

    @discord.ui.button(label='Close', style=discord.ButtonStyle.red)
    async def close(self, button, interaction):
        embed = Embed(title="Bye bye!",
            colour=discord.Colour.red())
        embed.set_footer(text="closing in 5 seconds")

        await interaction.message.edit(embed=embed, delete_after=5, view=None)        
        self.stop()

    @staticmethod
    async def read(file):
        lang = file.filename.split('.')[-1]
        if lang:
            try:
                content = (await file.read()).decode('utf-8', 'strict').replace('\r', '').replace('        ', '\t')
                return (lang, content)

            except UnicodeDecodeError:
                pass

    @staticmethod
    def response_embed(embed: Embed, status: int, response: dict[Any] = None) -> Embed:
        if status == 500:
            embed.description = 'There was an error reading your file. Try again'
            embed.colour = Colour.red()

        elif status == 102:
            embed.description = 'Running your program...'
            embed.colour = Colour.yellow()

        elif status == 200:
            desc = '✅: correct\n🛑: wrong answer\n ⚠️: error\n\n'
            for test_case in response['trace']:
                case_results = []
                for case in test_case['responses']:
                    if 'Traceback' in case['got']:
                        case_results.append('⚠️')
                        if test_case['test case'] == 0 and case['case'] == 0:
                            desc = case['got']
                    
                    elif case['correct']:
                        case_results.insert(case['case'], '✅')
                            
                    elif not case['correct']:
                        case_results.insert(case['case'], '🛑')

                if 'Traceback' not in desc:
                    desc += ' '.join(case_results) + "\n"

            desc += f"\nPoints earned: {response['points']}"
            embed.description = desc

            if '⚠️' in desc[39:] or '🛑' in desc[39:] or 'Traceback' in desc:
                embed.colour = Colour.red()

            else:
                embed.colour = Colour.green()

        return embed

    @staticmethod
    def run_file(file_info: tuple[str], user_id: int, problem_id: int) -> Dict[str, Any]:
        json = {
            "key": '7e8e71c8-0308-4dcc-b09e-2b00dbec60c9', # TODO replace this with a env variable
            "icode": file_info[1],
            "idiscordid": str(user_id),
            "problemid": str(problem_id),
        }

        lang = file_info[0]
        if lang == 'py':
            json['ilanguage'] = 'python3'
            json['iversion'] = '3.9.4'
            json['iextension'] = 'py'

        elif lang == 'java':
            json['ilanguage'] = 'java'
            json['iversion'] = '15.0.2'
            json['iextension'] = ''

        elif lang == 'cpp':
            json['ilanguage'] = 'c++'
            json['iversion'] = '10.2.0'
            json['iextension'] = ''
        
        response = requests.post("https://codingcomp.netlify.app/api/bot/solve", json=json)
        return response.json()

    async def disable_submission(self, interaction) -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.label == 'Submit':
                    child.disabled = True

        await interaction.message.edit(view=self)