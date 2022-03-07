from random import choice
import asyncio

import discord

from .feature_cog import Feature
from ..for_friends.pick_friend_view import PickFriendView

class MazeCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'maze', MazeView)

class MazeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Race to the Bathroom", style=discord.ButtonStyle.blurple, custom_id='maze')
    async def solve_a_maze(self, button, interaction):
        view = PickFriendView(interaction.guild.members)
        await interaction.response.send_message('\u200b', view=view, ephemeral=True)
        await view.wait()

        if view.friend:
            p1_info = {}
            p2_info = {}
            
            p1 = interaction.user
            p1_info['player'] = p1

            # getting player 2
            p2 = view.friend
            p2_info['player'] = p2
            
            # creating mazes
            # TODO allow people to decide on a size
            m1 = Maze(size=int(14))
            m2 = Maze(size=int(14))

            p1_info['maze'] = m1
            p2_info['maze'] = m2

            # asking player two if they want to play
            accept_view = AcceptView()
            await p2.send("You hear fast small steps in the middle of the night, seems like someone is going to the bathroom, and fast... You suddenly feel an urge to poop.",
                view=accept_view)
            await accept_view.wait()
            if accept_view.accepted:
                await p1.send("You hear someone getting up. You pick up your pace to make sure you get to the bathroom!")
                
                # creating games views
                v1 = GameView(p1, m1)
                v2 = GameView(p2, m2)
                
                # sending game views to users
                msg1 = await p1.send(str(m1), view=v1)
                msg2 = await p2.send(str(m2), view=v2)
                p1_info['msg'] = msg1
                p2_info['msg'] = msg2

                # waiting for someone to be done
                done, pending = await asyncio.wait([
                    asyncio.create_task(v1.wait(), name='v1'),
                    asyncio.create_task(v2.wait(), name='v2')
                ], return_when=asyncio.FIRST_COMPLETED)
                first = done.pop()

                await v1.disable(msg1)
                await v2.disable(msg2)

                # deterining who won
                if first.get_name() == 'v1':
                    winner = p1_info
                    loser = p2_info
                else:
                    winner = p2_info
                    loser = p1_info

                # pooping everywhere
                loser['maze'].poop()
                await loser['msg'].edit(content=str(loser['maze']))

                # sending messages
                won_message = 'Congratulations, you made it to the bathroom first!'
                lost_message = 'You pooped your pants, someone else got to the bathroom first!'
                await winner['player'].send(content=won_message)
                await loser['player'].send(content=lost_message)

                # sending messages to the original channel
                await interaction.channel.send(f"{winner['player'].name} got to the bathroom before {loser['player'].name}, who unfortunately pooped his pants!\n\nGame Stats", delete_after=20)
                await interaction.channel.send(f"{winner['player'].name}'s Maze\n{winner['maze']}", delete_after=20)
                await interaction.channel.send(f"{loser['player'].name}'s Maze (of course it has poop everywhere)\n{loser['maze']}", delete_after=20)

            else:
                await p1.send(f"Luckily you were quiet enough and did not wake up {p2.name}, you have the bathroom all to yourself.")

class AcceptView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        self.accepted = False

    @discord.ui.button(label='Wake Up', style=discord.ButtonStyle.green)
    async def accept(self, button, interaction):
        self.accepted = True
        await self.stop(interaction)
        await interaction.response.send_message(content="As you get up from the bed, the steps get louder and faster... You have to get up quick and run to the bathroom!")

    @discord.ui.button(label='Hold it In', style=discord.ButtonStyle.red, row=2)
    async def refuse(self, button, interaction):
        await self.stop(interaction)
        await interaction.response.send_message(content="You remembered you have diapers on, so you decide to go back to sleep.")

    async def stop(self, interaction):
        super().stop()

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(view=self)

class GameView(discord.ui.View):
    def __init__(self, p: discord.Member, maze):
        super().__init__(timeout=None)
        
        self.p: discord.Member = p
        self.maze: Maze = maze

        directions = [('up', 1), ('down', 2), ('left', 1), ('right', 2)]
        for direction, row in directions:
            self.add_item(DirectionButton(direction, row))

    def won(self):
        if self.maze.maze[-1][-1].state == 'occupied':
            self.stop()

    async def disable(self, msg):
        self.stop()

        for child in self.children:
            child.disabled = True

        await msg.edit(view=self)

class DirectionButton(discord.ui.Button):
    def __init__(self, direction: str, row: int):
        super().__init__(style=discord.ButtonStyle.blurple,
            label=direction.capitalize(),
            row=row)

        self.direction = direction

    async def callback(self, interaction):
        self.view.maze.move(self.direction)
        await interaction.response.edit_message(content=str(self.view.maze))
        self.view.won()

class Maze:
    def __init__(self, size: int = 10):
        self.size = size if size < 14 else 14
        
        self.maze: list[list[Block]] = [[] for i in range(self.size)]
        self.blocks: dict[Coordinate, Block] = {}
        self.occupied: Coordinate = Coordinate(i=0, j=0)

        self.generate()

    def generate(self) -> None:
        self.add_blocks()
        self.create_path()
        self.fill_maze()

    def add_blocks(self) -> None:
        for i in range(self.size):
            for j in range(self.size):
                coord = Coordinate(i=i, j=j)
                block = Block(coord)
                self.maze[j].append(block)
                self.blocks[coord] = block

    def create_path(self) -> None:
        current = self.maze[0][0]
        current.state = 'empty'
        while current != self.maze[-1][-1]:
            direction = choice(['down', 'right'])
            coord = current.coord.move(direction)
            if coord in self.blocks:
                current = self.blocks[coord]
                self.blocks[coord].state = 'empty'

    def fill_maze(self) -> None:
        for block in self.blocks.values():
            if block.state == 'null':
                block.state = choice(['blocked', 'blocked', 'empty', 'empty', 'empty'])

        self.maze[0][0].state = 'occupied'
        self.maze[-1][-1].state = 'end'

    def move(self, direction: str) -> None:
        new_block = self.get_block(self.occupied.move(direction))
        if new_block and new_block.state != 'blocked':
            self.blocks[self.occupied].state = 'visited'
            new_block.state = 'occupied'
            self.occupied = new_block.coord

    def get_block(self, coord):
        if coord in self.blocks:
            return self.blocks[coord]

    def poop(self) -> None:
        for block in self.blocks.values():
            if block.state == 'empty':
                block.state = 'visited'

    def __str__(self) -> str:
        s = ""
        for row in self.maze:
            for block in row:
                s += str(block)

            s += '\n'

        return s

class Coordinate:
    def __init__(self, i: int = -1, j: int = -1):
        self.i: int = i
        self.j: int = j
    
    def move(self, direction: str):
        if direction == 'down':
            return Coordinate(self.i, self.j+1)

        elif direction == 'right':
            return Coordinate(self.i+1, self.j)

        elif direction == 'left':
            return Coordinate(self.i-1, self.j)

        elif direction == 'up':
            return Coordinate(self.i, self.j-1)

    def __eq__(self, other) -> bool:
        return self.i == other.i and self.j == other.j

    def __hash__(self) -> hash:
        return hash((self.__class__, self.i, self.j))

class Block:

    states = {'null': '🟥', 'empty': '⬛', 'blocked': '⬜',
        'occupied': '🏃', 'visited': '💩', 'end': '🚽'}

    def __init__(self, coord: Coordinate,
        state: str = 'null'):
        
        self.coord: Coordinate = coord
        self.state: str = state

    def __str__(self) -> str:
        return self.states[self.state]

    def __eq__(self, other) -> bool:
        return (self.coord == other.coord
                and self.state == other.state)
                
def setup(bot):
    bot.add_cog(MazeCommands(bot))