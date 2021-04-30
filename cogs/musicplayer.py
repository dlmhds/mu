import wavelink
from discord.ext import commands

class AlreadyConnected(commands.CommandError): pass

class NoVoiceChannelGiven(commands.CommandError): pass

class Player(wavelink.Player):
    def __init__(self,*args,**kwargs):
        super.__init__(*args,**kwargs)

    async def connect(self,ctx,channel):
        if self.is_connected:
            raise AlreadyConnected
        if not ctx.author.voice:
            raise 
        await super().connect(channel.id)

    async def teardown(self):
        try:
            await self.destroy()
        except:
            pass


