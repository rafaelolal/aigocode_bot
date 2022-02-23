import sqlite3
import os
from typing import List, Tuple, Union

from discord.ext import commands

class DB(commands.Cog):
    
    path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(path + '/' + 'aigocode.db')
    # conn = sqlite3.connect(":memory:")

    c = conn.cursor()

    channel_index_offset = 1
    channels = ['stats',
        'singleplayer', 'singleplayer_board',
        'versus', 'versus_board',
        'coop', 'coop_board',
        'tictactoe', 'tictactoe_board',
        'help', 'help_board']

    def __init__(self, bot):
        self.bot = bot
  
    @commands.command()
    async def create_guilds_table(self, ctx) -> None:
        with DB.conn:
            DB.c.execute(f"""CREATE TABLE guilds
                (id integer,
                 stats text,
                 singleplayer text,
                 singleplayer_board text,
                 versus text,
                 versus_board text,
                 coop text,
                 coop_board text,
                 tictactoe text,
                 tictactoe_board text,
                 help text,
                 help_baord text,
                 warnings integer)""")

    @commands.command()
    async def create_members_table(self, ctx) -> None:
        with DB.conn:
            DB.c.execute(f"""CREATE TABLE members
                (id integer,
                 singeplayer_wins integer,
                 versus_wins integer,
                 coop_wins integer,
                 tictactoe_wins integer,
                 helped integer)""")

    #######################################################################

    @staticmethod
    def add_guild(id: int) -> None:
        with DB.conn:
            DB.c.execute("INSERT INTO guilds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id, ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", 0,))

    @staticmethod
    def remove_guild(id: int) -> None:
        with DB.conn:
            DB.c.execute("DELETE FROM guilds WHERE id=?",
                (id,))

    @staticmethod
    def update_guild(id: int, field: str, value: Union[str, int]) -> None:
        with DB.conn:
            DB.c.execute(f"""UPDATE guilds SET {field}=? WHERE id=?""",
                (value, id))

    @staticmethod
    def get_channel(guild_id: int, channel_name: str) -> Tuple[int]:
        with DB.conn:
            DB.c.execute("""SELECT * FROM guilds WHERE id=?""",
                (guild_id,))
 
            guild = DB.c.fetchone()
            channel_id, msg_id = guild[DB.channels.index(channel_name) \
                + DB.channel_index_offset].split(', ')
            
            # TODO this if-statement is horrible
            if channel_id and msg_id:
                return int(channel_id), int(msg_id)

            return channel_id, msg_id

    #######################################################################

    @staticmethod
    def add_member(id: int) -> None:
        with DB.conn:
            DB.c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?)",
                (id, 0, 0, 0, 0, 0))

    @staticmethod
    def remove_member(id: int) -> None:
        with DB.conn:
            DB.c.execute("DELETE FROM members WHERE id=?",
                (id,))

    #######################################################################
    
    @staticmethod
    def fetch_all_members() -> List[List[int]]:
        with DB.conn:
            DB.c.execute("SELECT * FROM members")
            members = DB.c.fetchall()

            return members

    @staticmethod
    def fetch_one(id: int) -> Union[List[Union[str, int]], None]:
        with DB.conn:
            DB.c.execute("SELECT * FROM members WHERE id=?",
                (id,))

            member = DB.c.fetchone()

            DB.c.execute("SELECT * FROM guilds WHERE id=?",
                (id,))

            guild = DB.c.fetchone()

            if member:
                return member
            elif guild:
                return guild

def setup(bot):
    bot.add_cog(DB(bot))