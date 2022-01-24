import sqlite3
import os

from discord.ext import commands

# TODO create decorator call with_conn to avoid having to use a with statement everywhere

class DB(commands.Cog):
    
    path = os.path.dirname(os.path.realpath(__file__))
    conn = sqlite3.connect(path + '/' + 'aigocode.db')
    # conn = sqlite3.connect(":memory:")

    c = conn.cursor()

    def __init__(self, bot):
        self.bot = bot
  
    @staticmethod
    def create_guild_table(guild_id: int) -> None:
        with DB.conn:
            DB.DB.c.execute(f"""CREATE TABLE {guild_id}
                (members text,
                 stats integer,
                 singeplayer integer,
                 singeplayer_board integer,
                 versus integer,
                 versus_board integer,
                 coop integer,
                 coop_board integer,
                 tictactoe integer,
                 tictactoe_board integer,
                 help text,
                 help_baord integer,
                 congratulations integer,
                 warnings integer)""")

    def create_member_table() -> None:
        with DB.conn:
            DB.DB.c.execute(f"""CREATE TABLE members
                        (id integer,
                         guild integer,
                         singeplayer_wins integer,
                         versus_wins integer,
                         coop_wins integer,
                         tictactoe_wins integer,
                         helped integer)""")
    
    @staticmethod
    def add_member(id: int, guild: int) -> None:
        with DB.conn:
            DB.c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id, guild, 0, 0, 0, 0, 0))

    @staticmethod
    def remove_member(id):
        with DB.conn:
            DB.c.execute("DELETE FROM members WHERE id=?",
                (id,))

            DB.c.execute("SELECT * FROM evaluators WHERE id=?",
                (id,))
            
            evaluator = DB.c.fetchone()
            if evaluator:
                DB.c.execute("DELETE FROM evaluators WHERE id=?",
                    (id,))


    @staticmethod
    def update_member_name(id, name):
        with DB.conn:
            DB.c.execute("""UPDATE members SET name=? WHERE id=?""",
                        (name, id))

    #######################################################################
    
    @staticmethod
    def fetch_all():
        with DB.conn:
            DB.c.execute("SELECT * FROM members")
            members = DB.c.fetchall()

            return members

    @staticmethod
    def fetch_one(id):
        with DB.conn:
            DB.c.execute("SELECT * FROM members WHERE id=?",
                (id,))

            return DB.c.fetchone()

def setup(bot):
    bot.add_cog(DB(bot))