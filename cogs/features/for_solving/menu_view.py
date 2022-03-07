import discord
from discord import Embed

from .menu_items import MenuSelect, LoginButton
from cogs.db.mongodb import Mongo
from .problem_view import ProblemView

class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuSelect())
        self.problem_selected = None

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Begin!', style=discord.ButtonStyle.green, row=2)
    async def begin(self, button, interaction):
        if self.problem_selected:
            if not Mongo.db['Users'].count_documents(
                {'discordid': str(interaction.user.id)}, limit = 1):
                
                self.clear_items()

                self.add_item(LoginButton(interaction.user.id))
                self.add_item(button)

                await interaction.response.edit_message(embed=self.response_embed(401),
                    view=self)

            else:
                view = ProblemView(self, self.problem_selected['_id'])
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
        problem = self.problem_selected
        
        if status == 307:
            if problem and not remove_problem:
                embed = Embed(title=problem['title'],
                    url=f"https://www.aigocode.org/p/{problem['_id']}",
                    colour=discord.Colour.yellow())

                embed.add_field(name='Difficulty',
                    value=problem['difficulty'])
                
                embed.add_field(name='Tags',
                    value=self.f_tags(problem['tags']))

                if len(problem['description']) > 1024:
                    desc = "Sorry, the description of this problem is too long to be dislpayed in Discord. Click on the title to visit this problem at aigocode.org."

                else:
                    desc = problem['description']
                
                embed.add_field(name='Description',
                    value=desc,
                    inline=False)

            else:
                self.problem_selected = None

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
                url=f"https://www.aigocode.org/p/{problem['_id']}",
                description="Attach a file and press submit. Your results for each test case will appear here.",
                colour=discord.Colour.light_grey())

            embed.set_footer(text='Remember to close before starting another problem')

            embed.add_field(name='Difficulty',
                value=problem['difficulty'])
            
            embed.add_field(name='Tags',
                value=self.f_tags(problem['tags']))
            
            # TODO repeated code from status 307
            if len(problem['description']) > 1024:
                desc = "Sorry, the description of this problem is too long to be dislpayed in Discord. Click on the title to visit this problem at aigocode.org."

            else:
                desc = problem['description']
            
            embed.add_field(name='Description',
                value=desc,
                inline=False)
            
            for i, sample in enumerate(problem['samples']['inAndOut']):
                embed.add_field(name=f"Sample Input",
                    value=sample[0])
                embed.add_field(name=f"Sample Output",
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
    def f_tags(tags: list[str]) -> str:
        return ', '.join(tags)