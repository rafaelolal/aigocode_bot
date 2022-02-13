from math import ceil

import discord

from cogs.db.mongodb import Mongo

class ProblemMenuSelect(discord.ui.Select):
    def __init__(self):
        self.problems = [problem for problem in Mongo.db['Problems'].find()]
        self.page = 1
        options = [discord.SelectOption(label=problem['title'],
            description=', '.join(problem['tags'])) for problem in self.problems[:25]]

        super().__init__(placeholder='Pick a problem',
            min_values=1, max_values=1,
            options=options, row=0)

    async def callback(self, interaction):
        self.view.is_problem_selected = True
        await interaction.response.edit_message(embed=self.view.create_embed(0))

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