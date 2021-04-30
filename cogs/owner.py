from discord.ext import commands
import discord

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        embedmaker = self.bot.get_cog("EmbedMaker")
        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            embed = await embedmaker.embed(ctx,description=f'**`ERROR:`** {type(e).__name__} - {e}')
            await ctx.send(embed=embed)
        else:
            embed = await embedmaker.embed(ctx,description='**`SUCCESS`**')
            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        embedmaker = self.bot.get_cog("EmbedMaker")
        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            embed = await embedmaker.embed(ctx,description=f'**`ERROR:`** {type(e).__name__} - {e}')
            await ctx.send(embed=embed)
        else:
            embed = await embedmaker.embed(ctx,description='**`SUCCESS`**')
            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        embedmaker = self.bot.get_cog("EmbedMaker")
        try:
            self.bot.unload_extension(f'cogs.{cog}')
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            embed = await embedmaker.embed(ctx,description=f'**`ERROR:`** {type(e).__name__} - {e}')
            await ctx.send(embed=embed)
        else:
            embed = await embedmaker.embed(ctx,description='**`SUCCESS`**')
            await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        embed = await embedmaker.embed(ctx,description="**Signing off!**")
        await ctx.send(embed=embed)
        await ctx.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatepresence(self,ctx,*,presence: str):
        await self.bot.change_presence(activity=discord.Activity(name=presence,type=discord.ActivityType.watching))

def setup(bot):
    bot.add_cog(Owner(bot))