from math import ceil

import discord

from cogs.db.mongodb import Mongo

class MenuSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder='Pick a problem',
            min_values=1, max_values=1,
            options=options, row=0)

        self.problems = [problem for problem in Mongo.db['Problems'].find()]
        self.page = 1
        options = [discord.SelectOption(label=problem['title'],
            description=', '.join(problem['tags'])) for problem in self.problems[:25]]

        if len(self.problems) > 25:
            self.view.add_item(ScrollButton('up'))
            self.view.add_item(ScrollButton('down'))

    async def callback(self, interaction):
        self.view.problem_selected = self.get_problem()
        await interaction.response.edit_message(embed=self.view.response_embed(307))

    def get_problem(self) -> str:
        if self.values:
            info = [problem for problem in self.problems if problem['title'] == self.values[0]]
            return info[0]

    def scroll(self, direction: str) -> bool:
        scrolled = False
        if direction == 'up' and self.page != 1:
            scrolled = True
            self.page -= 1

        elif direction == 'down' and self.page < ceil(len(self.problems)/25):
            scrolled = True
            self.page += 1

        if scrolled:
            self.options = [discord.SelectOption(label=problem['title'],
                description=', '.join(problem['tags'])) for problem in self.problems[25*(self.page-1):25*self.page]]

        else:
            self.values.clear()

        return scrolled

class ScrollButton(discord.ui.Button):
    def __init__(self, direction: str):
        super().__init__(style=discord.ButtonStyle.blurple, label=direction.capitalize())
        self.direction = direction

    async def callback(self, interaction):
        select = self.view.get_select()
        scrolled = select.scroll(self.direction)
        await interaction.response.edit_message(embed=self.view.response_embed(307,
            remove_problem=scrolled),
            view=self.view)

class LoginButton(discord.ui.Button):
    
    MY_API = 'http://discord.thinkland.ai/api/'
    AUTH_API = f'https://dev-mcy9agvp.jp.auth0.com/authorize?response_type=code&scope=openid%20profile&state=STATE&client_id=XHVbOGXvGnLbDPh8ZO1IraTNTfgXPF6i&redirect_uri={MY_API}?id='

    def __init__(self, member_id):
        super().__init__(style=discord.ButtonStyle.green, label='Login', url=self.AUTH_API+str(member_id))