import discord
from discord.ext import commands

class EmbedMaker(commands.Cog):
    def __init__ (self,bot):
        self.bot = bot

    async def embed(self,ctx = None,title: str='',description: str='',url: str=''):
        color = discord.Colour(0xAC5C28)
        embed = discord.Embed(title=title,description=description,color=color,url=url)
        return embed

def setup(bot):
    bot.add_cog(EmbedMaker(bot))