import discord
from discord.ext import commands
import asyncio
import json

with open("data/config.json",'r') as f:
    config = json.load(f)
token = config['DiscordToken']

def get_prefix(bot,message):
    prefixes = ['m.','>>']
    #only uses .m in dms
    if not message.guild:
        return 'm.'
    #allows for use of multiple prefixes
    return commands.when_mentioned_or(*prefixes)(bot,message)

#list of all extensions
initial_extensions = [
    #cogs are here cogs.filename
    'cogs.owner',
    'cogs.embedmaker',
    'cogs.help',
    'cogs.error',
    #'cogs.musicquiz',
    'cogs.reply'
    
    
]

bot = commands.Bot(command_prefix = get_prefix, description = "shooting the deer")

#remove default help function
bot.remove_command('help')

#loads extensions
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(activity = discord.Activity(name="the concentration camps",type=discord.ActivityType.watching))

bot.run(token)