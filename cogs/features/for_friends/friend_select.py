from math import ceil

import discord

class FriendSelect(discord.ui.Select):
    def __init__(self, members):
        self.members = members
        self.page = 1

        options = [discord.SelectOption(label=f"{member.name}#{member.discriminator}",
            description=member.nick) for member in self.members[:25]]

        super().__init__(placeholder='Pick a friend',
            min_values=1, max_values=1,
            options=options, row=0)

    # TODO repeated code form menu_items
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