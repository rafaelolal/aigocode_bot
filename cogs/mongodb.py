import os
from dotenv import load_dotenv
import pymongo

from discord.ext import commands

load_dotenv()

class MongoDB(commands.Cog):

    db_name = 'CodingComp'
    client = pymongo.MongoClient(f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASS')}@cluster0.zfdpu.mongodb.net/CodingComp?retryWrites=true&w=majority")[db_name]
    
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(MongoDB(bot))