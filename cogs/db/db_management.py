import sqlite3
import pathlib
from typing import List, Tuple, Union

from discord.ext import commands

class DB(commands.Cog):
    
    path = pathlib.Path(__file__).parent.resolve()
    conn = sqlite3.connect(path / 'aigocode.db')
    # conn = sqlite3.connect(":memory:")

    c = conn.cursor()

    channels = ['stats',
        'singleplayer', 'singleplayer_board',
        'versus', 'versus_board',
        'coop', 'coop_board',
        'tictactoe', 'tictactoe_board',
        'maze', 'maze_board',
        'help', 'help_board',
        'display']

    PROJECTS = 1

    def __init__(self, bot):
        self.bot = bot
  
    @commands.command()
    @commands.is_owner()
    async def create_guilds_table(self, ctx) -> None:
        with DB.conn:
            DB.c.execute(f"""CREATE TABLE guilds
                (stats text,
                 singleplayer text,
                 singleplayer_board text,
                 versus text,
                 versus_board text,
                 coop text,
                 coop_board text,
                 tictactoe text,
                 tictactoe_board text,
                 maze text,
                 maze_board text
                 help text,
                 help_baord text,
                 display text,
                 warnings integer,
                 id integer)""")

    @commands.command()
    @commands.is_owner()
    async def create_members_table(self, ctx) -> None:
        with DB.conn:
            DB.c.execute(f"""CREATE TABLE members
                (id integer,
                 projects text,
                 singeplayer_wins integer,
                 versus_wins integer,
                 coop_wins integer,
                 tictactoe_wins integer,
                 maze_wins integer,
                 helped integer)""")

    #######################################################################

    @staticmethod
    def add_guild(id: int) -> None:
        with DB.conn:
            DB.c.execute("INSERT INTO guilds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", ", 0, id,))

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
            guild = DB.fetch_one(guild_id)
            channel_id, msg_id = guild[DB.channels.index(channel_name)].split(', ')
            
            if channel_id and msg_id:
                return int(channel_id), int(msg_id)

            return None, None

    #######################################################################

    @staticmethod
    def add_member(id: int) -> None:
        with DB.conn:
            DB.c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id, ' ', 0, 0, 0, 0, 0, 0))

    @staticmethod
    def remove_member(id: int) -> None:
        with DB.conn:
            DB.c.execute("DELETE FROM members WHERE id=?",
                (id,))

    @staticmethod
    def get_user_by_project(message_id: int) -> List:
        with DB.conn:
            DB.c.execute("SELECT * FROM members WHERE projects LIKE ?",
            (f"%{message_id}%",))
        
        return DB.c.fetchone()

    @staticmethod
    def add_project_to_user(user_id: int, message_id: int) ->  None:
        with DB.conn:
            user = DB.fetch_one(user_id)

            if user[DB.PROJECTS]:
                projects = user[DB.PROJECTS] + f", {message_id}"

            else:
                projects = f"{message_id}"

            DB.c.execute("UPDATE members SET projects=? WHERE id=?", (projects, user_id,))

    @staticmethod
    def remove_project_from_user(user_id: int, message_id: int) -> None:
        with DB.conn:
            DB.c.execute("SELECT * FROM members WHERE id=?", (user_id,))
            user = DB.c.fetchone()

            projects = user[DB.PROJECTS].split(', ')
            if str(message_id) not in projects:
                raise ValueError(f"user with user_id {user_id} does not contain project with message_id {message_id}")

            projects.remove(str(message_id))
            
            DB.c.execute("UPDATE members SET projects=? WHERE id=?", (', '.join(projects), user_id,))

    #######################################################################
    
    @commands.command()
    @commands.is_owner()
    async def fetch_all_members(self, ctx) -> List[List[int]]:
        with DB.conn:
            DB.c.execute("SELECT * FROM members")
            members = DB.c.fetchall()

            # print('\n'.join(map(str, members)))
            return members

    @commands.command()
    @commands.is_owner()
    async def fetch_all_guilds(self, ctx) -> List[List[int]]:
        with DB.conn:
            DB.c.execute("SELECT * FROM guilds")
            guilds = DB.c.fetchall()

            # print('\n'.join(map(str, guilds)))
            return guilds

    @staticmethod
    def fetch_one(id: int) -> Union[list[Union[str, int]], None]:
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