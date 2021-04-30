import discord
from discord.ext import commands

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        embedmaker = self.bot.get_cog("EmbedMaker")
        #resets cooldowns
        # try:
        #     ctx.command.reset_cooldown(ctx)
        # except Exception as e:
        #     print(e)
        #error catching and responses
        if isinstance(error, commands.CheckFailure):
            embed = await embedmaker.embed(ctx,title="Permission Error",description="You do no have permission to run this command")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            embed = await embedmaker.embed(ctx,title="Command does not exist",description="Type `m.help` for a full list of commands")
            await ctx.send(embed=embed)
        elif isinstance(error,commands.MissingRequiredArgument):
            embed = await embedmaker.embed(ctx,title="Error",description=f"You are missing `<{error.param}>` from your command\nType `m.help command` for more info")
            embed.set_footer(text='<> are required arguments, [] are optional arguments')
            await ctx.send(embed=embed)
        elif isinstance(error,commands.CommandOnCooldown):
            embed = await embedmaker.embed(ctx,title="Cooldown",description=f"Try again in {error.retry_after:.2f}s")
            embed.set_footer(text=f'There is a {error.cooldown.per:.2f}s cooldown for this command')
            await ctx.send(embed=embed)
        elif isinstance(error,commands.BadArgument):
            embed = await embedmaker.embed(ctx,title="Error",description=str(error))
            await ctx.send(embed=embed)
        elif isinstance(error,commands.CommandInvokeError):
            embed = await embedmaker.embed(ctx,title="Error",description=str(error))
            await ctx.send(embed=embed)
        elif isinstance(error,commands.BadUnionArgument):
            embed = await embedmaker.embed(ctx,title="Error, Invalid Argument!",description=f'{error.param} must be {error.converters}')
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{type(error).__name__} - {error}')

def setup(bot):
    bot.add_cog(Error(bot))