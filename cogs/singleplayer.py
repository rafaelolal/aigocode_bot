from math import ceil

import discord
from discord.embeds import Embed
from discord.ext import commands

from cogs.mongodb import MongoDB
from cogs.helpers import Helpers
from db.db_management import DB

class SingleplayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def add_singleplayer(self, ctx):
        channel_id, message_id = DB.get_channel(ctx.guild.id, 'singleplayer')
        if not channel_id:
            msg = await ctx.send('\u200b', view=PlaySingleplayer(self.bot))
            DB.update_guild(ctx.guild.id, "singleplayer", f"{ctx.channel.id}, {msg.id}")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This channel already has this feature.")
            
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def remove_singleplayer(self, ctx):
        channel_id, msg_id = DB.get_channel(ctx.guild.id, "singleplayer")
        message = await Helpers.get_message(ctx, msg_id)
        if message:
            await message.delete()
            DB.update_guild(ctx.guild.id, "singleplayer", ", ")

        else:
            embed = Helpers.warning_embed("Invalid Action",
                "This feature is not present")
    
            await ctx.send(embed=embed, delete_after=5)

class PlaySingleplayer(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.playing_now = []

    async def interaction_check(self, interaction):
        return interaction.user not in self.playing_now

    @discord.ui.button(label='Play Singleplayer', style=discord.ButtonStyle.blurple, custom_id='play_singleplayer')
    async def play_singleplayer(self, button, interaction):
        await interaction.response.defer()
        
        self.playing_now.append(interaction.user)
        view = ProblemMenuView(self.bot)
        await interaction.user.send(embed=view.create_embed(0), view=view)
        await view.wait()
        self.playing_now.remove(interaction.user)

class ProblemMenuView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(ProblemMenuSelect())

    # async def interaction_check(self, interaction):
    #     pass

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label='Up', style=discord.ButtonStyle.blurple, row=1)
    async def up(self, button, interaction):
        select = self.get_select()
        scrolled = select.scroll('up')
        await interaction.response.edit_message(embed=self.create_embed(0, remove_problem=scrolled), view=self)

    @discord.ui.button(label='Down', style=discord.ButtonStyle.blurple, row=2)
    async def down(self, button, interaction):
        select = self.get_select()
        scrolled = select.scroll('down')
        await interaction.response.edit_message(embed=self.create_embed(0, remove_problem=scrolled), view=self)

    @discord.ui.button(label='Begin!', style=discord.ButtonStyle.green, row=2)
    async def begin(self, button, interaction):
        await interaction.message.edit(embed=self.create_embed(1), view=None, delete_after=5)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, row=1)
    async def cancel(self, button, interaction):
        await interaction.message.edit(embed=self.create_embed(2), view=None, delete_after=5)
        self.stop()

    def get_select(self):
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                return child

    def create_embed(self, status, remove_problem=False):
        if status == 0:
            select = self.get_select()
            problem = select.get_problem()
            if problem and not remove_problem:
                embed = Embed(title=problem['title'],
                    colour=discord.Colour.yellow())

                embed.add_field(name='Difficulty', value=problem['difficulty'])
                embed.add_field(name='Tags', value=self.f_tags(problem['tags']))
                embed.add_field(name='Description', value=problem['description'], inline=False)

            else:
                embed = Embed(title="AiGoCode",
                    colour=discord.Colour.blue())
            
                embed.add_field(name='No problem selected', value='\u200b')

            embed.set_footer(text=self.get_page_range())

        elif status == 1:
            embed = Embed(title="Problem has begun!",
                colour=discord.Colour.green())

        elif status == 2:
            embed = Embed(title="Bye bye!",
                colour=discord.Colour.red())

        if status != 0:
            embed.set_footer(text="menu will close in 5 seconds")

        return embed

    def get_page_range(self):
        select = self.get_select()
        page_range = f"{(select.page-1)*25} - {len(select.problems) if select.page*25 > len(select.problems) else select.page*25} of {len(select.problems)}"
        return page_range

    @staticmethod
    def f_tags(tags):
        return ', '.join(tags)

class ProblemMenuSelect(discord.ui.Select):
    def __init__(self):
        self.problems = [problem for problem in MongoDB.client['Problems'].find()]
        self.page = 1
        options = [discord.SelectOption(label=problem['title'], description=', '.join(problem['tags'])) for problem in self.problems[:25]]

        super().__init__(placeholder='Pick a problem', min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction):
        problem = self.get_problem()
        await interaction.response.edit_message(embed=self.view.create_embed(0))

    def get_problem(self):
        if self.values:
            info = [problem for problem in self.problems if problem['title'] == self.values[0]]
            return info[0]

    def scroll(self, direction):
        scrolled = False
        if direction == 'up' and self.page != 1:
            scrolled = True
            self.page -= 1

        elif direction == 'down' and self.page < ceil(len(self.problems)/25):
            scrolled = True
            self.page += 1

        if scrolled:
            self.options = [discord.SelectOption(label=problem['title'], description=', '.join(problem['tags'])) for problem in self.problems[25*(self.page-1):25*self.page]]

        else:
            self.values.clear()

        return scrolled

def setup(bot):
    bot.add_cog(SingleplayerCommands(bot))