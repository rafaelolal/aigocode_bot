from typing import List

import discord
from discord import Embed

from items.problem_menu_select import ProblemMenuSelect
from items.login_button import LoginButton
from cogs.db.mongodb import Mongo
from .solve_view import SolveView

class ProblemMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProblemMenuSelect())
        self.is_problem_selected = False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Up', style=discord.ButtonStyle.blurple, row=1)
    async def up(self, button, interaction):
        select = self.get_select()
        scrolled = select.scroll('up')
        await interaction.response.edit_message(embed=self.response_embed(307,
            remove_problem=scrolled),
            view=self)

    @discord.ui.button(label='Down', style=discord.ButtonStyle.blurple, row=2)
    async def down(self, button, interaction):
        select = self.get_select()
        scrolled = select.scroll('down')
        await interaction.response.edit_message(embed=self.response_embed(307,
            remove_problem=scrolled),
            view=self)

    @discord.ui.button(label='Begin!', style=discord.ButtonStyle.green, row=2)
    async def begin(self, button, interaction):
        if self.is_problem_selected:
            if not Mongo.db['Users'].count_documents(
                {'discordid': str(interaction.user.id)}, limit = 1):
                
                for child in self.children:
                    self.remove_item(child)

                self.add_item(LoginButton(interaction.user.id))
                self.add_item(button)

                await interaction.response.edit_message(embed=self.response_embed(401),
                    view=self)

            else:
                select = self.get_select()
                if select:
                    problem = select.get_problem()

                view = SolveView(self, problem['_id'])
                await interaction.user.send(embed=self.response_embed(201),
                    view=view)
                
                await interaction.response.edit_message(embed=self.response_embed(200),
                    view=None)
                
                await view.wait()

                self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, row=1)
    async def cancel(self, button, interaction):
        await interaction.response.edit_message(embed=self.response_embed(410),
            view=None)
        self.stop()        

    def get_select(self) -> discord.ui.Select:
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                return child

    def response_embed(self, status: int, remove_problem: bool = False) -> Embed:
        select = self.get_select()
        if select:
            problem = select.get_problem()
        if status == 307:
            if problem and not remove_problem:
                embed = Embed(title=problem['title'],
                    colour=discord.Colour.yellow())

                embed.add_field(name='Difficulty',
                    value=problem['difficulty'])
                
                embed.add_field(name='Tags',
                    value=self.f_tags(problem['tags']))
                
                embed.add_field(name='Description',
                    value=problem['description'],
                    inline=False)

            else:
                self.is_problem_selected = False

                embed = Embed(title="AiGoCode",
                    colour=discord.Colour.blue())
            
                embed.add_field(name='No problem selected',
                    value='\u200b')

            embed.set_footer(text=self.get_page_range())

        elif status == 200:
            embed = Embed(title="Problem has begun!",
                description="Go to your DMs!",
                colour=discord.Colour.green())

        elif status == 201:
            embed = Embed(title=problem['title'],
                description="Problem has begun!",
                colour=discord.Colour.light_grey())

            embed.add_field(name='Difficulty',
                value=problem['difficulty'])
            
            embed.add_field(name='Tags',
                value=self.f_tags(problem['tags']))
            
            embed.add_field(name='Description',
                value=problem['description'],
                inline=False)
            
            for i, sample in enumerate(problem['samples']['inAndOut']):
                embed.add_field(name=f"Sample {i} Input",
                    value=sample[0])
                embed.add_field(name=f"Sample {i} Output",
                    value=sample[1])

            embed.add_field(name='Explanation',
                value=problem['samples']['explanation'],
                inline=False)

        elif status == 410:
            embed = Embed(title="Bye bye!",
                colour=discord.Colour.red())

        elif status == 401:
            embed = Embed(title="Login",
                colour=discord.Colour.blue())

            embed.set_footer(text="Sorry for the inconvenience, but this is a one time thing")

        return embed

    def get_page_range(self) -> str:
        select = self.get_select()
        page_range = f"{(select.page-1)*25} - "
        if select.page*25 > len(select.problems):
            page_range += str(len(select.problems))

        else:
            page_range += str(select.page*25)

        page_range += f" of {len(select.problems)}"
        return page_range

    @staticmethod
    def f_tags(tags: List[str]) -> str:
        return ', '.join(tags)
