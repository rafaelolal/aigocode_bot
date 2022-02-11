import os
from dotenv import load_dotenv
import pymongo

from discord.ext import commands

load_dotenv()

class Mongo(commands.Cog):

    db = pymongo.MongoClient(
        f"mongodb://aigocode:{os.getenv('MONGO_SECRET')}==@aigocode.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@aigocode@") \
        ['CodingComp']
    
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Mongo(bot))