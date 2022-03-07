from math import ceil

import discord
from discord.ext import commands

from .feature_cog import Feature

class VersusCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'versus', VersusView)

    async def add_versus(self, ctx):
        await super().add_feature(ctx)

    async def remove_versus(self, ctx):
        await super().remove_feature(ctx)

class VersusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.playing_now = []

    async def interaction_check(self, interaction):
        if interaction.user in self.playing_now:
            await interaction.response.send_message("Finish solving the problem you already started or close it to start another", ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label='Play Versus', style=discord.ButtonStyle.blurple, custom_id='play_versus')
    async def play_versus(self, button, interaction):
        self.playing_now.append(interaction.user)
        view = FriendSelect()
        await interaction.response.send_message('\u200b',
            view=view,
            ephemeral=True)
    
        await view.wait()

        self.playing_now.remove(interaction.user)

class PickFriendView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(FriendSelect() )
    

    @discord.ui.button(label='Play Versus', style=discord.ButtonStyle.blurple, custom_id='play_versus')
    async def play_versus(self, button, interaction):
        self.playing_now.append(interaction.user)
        view = FriendSelect()
        await interaction.response.send_message('\u200b',
            view=view,
            ephemeral=True)
    
        await view.wait()

        self.playing_now.remove(interaction.user)

    @discord.ui.button(label='Play Versus', style=discord.ButtonStyle.blurple, custom_id='play_versus')
    async def play_versus(self, button, interaction):
        self.playing_now.append(interaction.user)
        view = FriendSelect()
        await interaction.response.send_message('\u200b',
            view=view,
            ephemeral=True)
    
        await view.wait()

        self.playing_now.remove(interaction.user)

class FriendSelect(discord.ui.Select):
    def __init__(self, members):
        self.members = members
        self.friend = None

        self.page = 1
        options = [discord.SelectOption(label=f"{member.name}#{member.discriminator}",
            description=member.nick) for member in self.members[:25]]

        super().__init__(placeholder='Pick a friend',
            min_values=1, max_values=1,
            options=options, row=0)

    async def callback(self, interaction):
        friend = self.values[0]
        name, disc = friend.split('#')
        for member in self.members:
            if member.name == name and member.discriminator == disc:
                self.friend = member
                break

        self.view.stop()
        await interaction.response.edit_message(view=None)


    def scroll(self, direction: str) -> bool:
        scrolled = False
        if direction == 'up' and self.page != 1:
            scrolled = True
            self.page -= 1

        elif direction == 'down' and self.page < ceil(len(self.members)/25):
            scrolled = True
            self.page += 1

        if scrolled:
            self.options = [discord.SelectOption(label=member.nick,
            description=member.name) for member in self.members[25*(self.page-1):25*self.page]]
        
        else:
            self.values.clear()

        return scrolled

def setup(bot):
    bot.add_cog(VersusCommands(bot))