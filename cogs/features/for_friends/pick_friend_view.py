import discord

from .friend_select import FriendSelect

class PickFriendView(discord.ui.View):
    def __init__(self, members):
        super().__init__(timeout=None)

        self.friend = None
        self.add_item(FriendSelect(members))
    
    @discord.ui.button(label='Begin', style=discord.ButtonStyle.green, row=2)
    async def begin(self, button, interaction):
        select = self.get_select()
        friend = select.values[0]
        name, disc = friend.split('#')
        for member in select.members:
            if member.name == name and member.discriminator == disc:
                self.friend = member
                break

        await self.disable(interaction)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, row=2)
    async def cancel(self, button, interaction):
        await self.disable(interaction)

    # TODO copied code from menu_view
    def get_select(self) -> discord.ui.Select:
        for child in self.children:
            if isinstance(child, discord.ui.Select):
                return child

    # TODO Copied code from display.py
    async def disable(self, interaction) -> None:
        for child in self.children:
            child.disabled = True

        self.stop()
        await interaction.response.edit_message(view=self)