import discord
from discord.ext import commands
import json
import re
import random

class Reply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open("data/replys.json", 'r') as f:
            jsondump = json.load(f)

        self.reply_database = jsondump
        self.chat_log = []

    @commands.Cog.listener()
    async def on_message(self,message):
        
        if message.author == self.bot.user:
            return

        if message.channel.id != 832335882097917973:
            return 
        #keep track of chat
        self.chat_log.append([message.content, message.author.id])
        #gets channel
        channel = self.bot.get_channel(message.channel.id)

        bot_reply = message.content
        
        await channel.send(bot_reply)
        self.chat_log.append([bot_reply,0])
        await channel.send(self.chat_log)

    @tasks.loop(seconds = 5)
    async def draw_connections(self):
        for i in range(0,len(chat_log)-1):
            mesage = chat_log[i][0]
            next_message = chat_log[i+1][0]
            if message not in self.word_database:
                






def setup(bot):
    bot.add_cog(Reply(bot))