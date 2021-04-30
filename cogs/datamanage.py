import json
import discord
from discord.ext import commands
import os
import random

class DataManage(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def edit_json(self,key: str,value,file):
        with open(file,'r') as f:
            jsondump = json.load(f)
        jsondump[key] = value
        tempfile = f'{key}-{random.randrange(0,100000)}.json'
        with open(tempfile,'w+') as f:
            json.dump(jsondump,f,indent=4)
        os.replace(tempfile,file)

    async def del_key(self,key: str,file):
        with open(file,'r') as f:
            jsondump = json.load(f)
        jsondump.pop(str(key))
        tempfile = f'{key}-{random.randrange(0,100000)}.json'
        with open(tempfile,'w+') as f:
            json.dump(jsondump,f,indent=4)
        os.replace(tempfile,file)


def setup(bot):
    bot.add_cog(DataManage(bot))