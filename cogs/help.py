import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def help(self,ctx,*,command: str=None):
        embedmaker = self.bot.get_cog("EmbedMaker")
        commandlist = []
        for x in self.bot.walk_commands():
            commandlist.append(x.name)
        if not command:
            embed = await embedmaker.embed(ctx,title="Commands Listing",description="**m.help <command name>** for more details")
            for x in self.bot.cogs:
                text = ''
                for y in self.bot.cogs[x].walk_commands():
                    if not y.hidden:
                        text = f'{text}\n{y.name}'
                if text != '':
                    embed.add_field(name=x,value=text)
            await ctx.send(embed=embed)
        elif command in self.bot.cogs:
            text = ''
            for y in self.bot.cogs[command].walk_commands():
                if not y.hidden:
                    text = f'{text}\n{y.name}'
            if text != '':
                embed = await embedmaker.embed(ctx,title=f"{command} Commands Listing",description="**m.help <command name>** for more details")
                embed.add_field(name="Commands",value=text)
                await ctx.send(embed=embed)
            else:
                embed = await embedmaker.embed(ctx,description=f"There are no commands under {command}")
                await ctx.send(embed=embed)
        elif command in commandlist:
            if not self.bot.get_command(command).hidden:
                embed = await embedmaker.embed(ctx,title=f"Help for m.{command}",description=self.bot.get_command(command).help)
                await ctx.send(embed=embed)
            else:
                embed = await embedmaker.embed(ctx,description=f"**{command}** does not exist")
                await ctx.send(embed=embed)
        else:
            embed = await embedmaker.embed(ctx,description=f"**{command}** does not exist")
            await ctx.send(embed=embed)            


def setup(bot):
    bot.add_cog(Help(bot))