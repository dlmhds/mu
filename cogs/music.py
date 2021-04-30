from discord.ext import commands, tasks
import discord
import validators
import youtube_dl
import json
from ytmusicapi import YTMusic 
import sys
import random
import os
#TODO reformat classes to make them more readable
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'm4a',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'outtmpl':'',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        filename = f"{random.randrange(0,10000000)}-{random.randrange(0,10000000)}.m4a"
        ytdl_format_options['outtmpl'] = f"{filename}"
        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        #filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        #position 0 -> currently playing
        #rest are order of queue
        self.queue = {}
        #0 - idle
        #1 - playing 
        #2 - music guessing
        #3 - paused
        self.state = {}

        self.ytmusic = YTMusic()

        self.currently_playing = {}

        #in the case of reloading cog
        for server in self.bot.guilds:
            self.queue[server] = [];
            self.state[server] = 0;
            self.currently_playing[server] = ""
        self.music_player.start()


    @commands.Cog.listener()
    async def on_ready(self):
        #initialize lists
        for server in self.bot.guilds:
            self.queue[server] = [];
            self.state[server] = 0;

    @tasks.loop(seconds = 0)
    async def music_player(self):
        for server in self.queue:

            # sys.stdout.write(f"\rstate: {self.state[server]}\nqueue: {self.queue[server]}")
            # sys.stdout.flush()

            #the state is in playing
            if self.state[server] == 1:
                #if there is nothing playing
                if server.voice_client is None or not server.voice_client.is_playing():
                    #checks if there is anything in queue
                    if len(self.queue[server]) > 1 and server.voice_client is not None:
                        #there is a song in queue
                        #removes the file
                        if self.queue[server][0] != "filler":
                            os.remove(f"{self.currently_playing[server]}")
                        self.queue[server].pop(0)
                        await self.play_song(self.queue[server][0],server)
                        
                    else:
                        #removes the file
                        os.remove(f"{self.currently_playing[server]}")
                        if server.voice_client is None:
                            #in the case bot is kicked from vc
                            self.queue[server] = []
                        else:
                            self.queue[server].pop(0)
                        #set state to idle
                        self.state[server] = 0
            elif self.state[server] == 0:
                #not active
                pass
            elif self.state[server] == 2:
                #guesser
                pass
            elif self.state[server] == 3:
                #paused
                pass

    #song_info = {'url':url_here, 'title': title_here, 'artists': [artists_here]}
    async def play_song(self,song_info,server,filename = None):
        #creates file
        if filename == None:
            filename = await YTDLSource.from_url(song_info['url'],loop = self.bot.loop)
        #plays file
        server.voice_client.play(discord.FFmpegOpusAudio(executable="ffmpeg.exe",source=f"{filename}"))
        #adds filename to currently_playing so it can be deleted later
        self.currently_playing[server] = filename


    #song_info = {'url':url_here, 'title': title_here, 'artists': [artists_here], 'duration': duration
    #              'thumbnail': thumbnail_url_here}
    async def get_formatted_embed(self,ctx,song_info):
        embedmaker = self.bot.get_cog("EmbedMaker")
        embed = await embedmaker.embed(ctx,description = f"[{song_info['title']}]({song_info['url']})")
        embed.add_field(name = "Artist(s)", value = song_info['artists'])
        embed.add_field(name = "Duration", value = song_info['duration'])
        embed.add_field(name = "Queue", value = self.queue[ctx.message.guild].index(song_info))
        embed.set_thumbnail(url = song_info['thumbnail'])
        return embed

    async def join_user_channel(self,ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    async def leave_voice_channel(self,ctx):
        server = ctx.message.guild.voice_client
        await server.disconnect()

    async def get_song(self,term):
        search_results = self.ytmusic.search(term,'songs')
        song_info = {}
        song_info['title'] = search_results[0]['title']
        song_info['url'] = f"http://www.youtube.com/watch?v={search_results[0]['videoId']}"
        song_info['duration'] = search_results[0]['duration']
        song_info['thumbnail'] = search_results[0]['thumbnails'][0]['url']
        artist = []
        for a in search_results[0]['artists']:
            artist.append(a['name'])
        song_info['artists'] = artist
        print(song_info)
        return song_info

    @commands.command(help='''joins current voice channel''')
    async def join(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        if ctx.message.author.voice:
            await self.join_user_channel(ctx)
            embed = await embedmaker.embed(ctx,description = f"Successfully joined *{ctx.author.voice.channel}*")
        else:
            #user not in voice channel
            embed = await embedmaker.embed(ctx,description = f"{ctx.author.mention} is not in a voice channel")
        await ctx.send(embed=embed)

    @commands.command(help='''leaves voice channel''',
                        aliases = ['dc','disconnect'])
    async def leave(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        current_server = ctx.message.guild
        voice = ctx.message.guild.voice_client
        if voice is None or not voice.is_connected():
            #bot not in voice channel
            embed = await embedmaker.embed(ctx,description = "Are you dumb?")
        elif ctx.author.voice.channel != voice.channel:
            embed = await embedmaker.embed(ctx,title = "Error",description = "You must be in the same voice channel")
        else:
            await self.leave_voice_channel(ctx)
            self.queue[current_server] = []
            embed = await embedmaker.embed(ctx,description = "Successfully disconnected")
        

        await ctx.send(embed = embed)

    @commands.command(help='''```play [song]```\nPlays song''')
    async def play(self,ctx,*,song: str):
        embedmaker = self.bot.get_cog("EmbedMaker")
        current_server = ctx.message.guild
        voice = ctx.message.guild.voice_client
        await ctx.send(song)
        if voice is not None and ctx.author.voice.channel != voice.channel:
            embed = await embedmaker.embed(ctx,title = "Error",description = "You must be in the same voice channel")
        elif self.state[current_server] == 2:
            embed = await embedmaker.embed(ctx,description = "Currently running music guesser!")
        else:
            voice = ctx.message.guild.voice_client
            if voice is None or not voice.is_connected():
                await self.join(ctx)
            #makes sure there is a voice channel it has joined
            if ctx.message.author.voice:
                song_info = await self.get_song(song)
                if len(self.queue[current_server]) == 0:
                    self.queue[current_server].append("filler")
                self.queue[current_server].append(song_info)
                embed = await self.get_formatted_embed(ctx,song_info)
                if len(self.queue[current_server]) > 1:
                    embed.set_author(name = "Added to Queue",icon_url = ctx.message.author.avatar_url)
                else:
                    embed.set_author(name = "Now Playing",icon_url = ctx.message.author.avatar_url)
                self.state[current_server] = 1 #set status to playing
            else:
                embed = await embedmaker.embed(ctx,description = "The sky is falling")
        await ctx.send(embed = embed)

    @commands.command(help='''pauses the song''')
    async def pause(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        voice = ctx.message.guild.voice_client
        current_server = ctx.message.guild
        if voice.is_playing() and self.state[current_server] == 1:
            voice.pause()
            self.state[current_server] = 3
            embed = await embedmaker.embed(ctx,description = "Paused")
        elif self.state[current_server] == 2:
            embed = await embedmaker.embed(ctx,description = f"Cannot pause during music guessing")
        else:
            embed = await embedmaker.embed(ctx,description = "There is nothing playing")
        await ctx.send(embed = embed)

    @commands.command(help='''resumes the song''')
    async def resume(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        voice = ctx.message.guild.voice_client
        current_server = ctx.message.guild
        if self.state[current_server] == 3:
            self.state[current_server] = 1
            voice.resume()
            #create function to format song data into print 
            embed = await self.get_formatted_embed(ctx,song_info)
        else:
            embed = await embedmaker.embed(ctx,description = "There is nothing to resume")
            embed.set_author(name = "Now Playing")
        await ctx.send(embed = embed)
            
    @commands.command(help='''skips the song''')
    async def skip(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        voice = ctx.message.guild.voice_client
        current_server = ctx.message.guild
        if self.state[current_server] == 0:
            embed = await embedmaker.embed(ctx,description = "There is nothing to skip!")
        elif self.state[current_server] == 2:
            pass
            #add implementation when skipping for guess
        else:
            print(voice.is_playing())
            embed = await embedmaker.embed(ctx,description = "Skipped")
            voice.stop()

        await ctx.send(embed = embed)

    async def format_song(self,song_info):
        artists = ""
        print(song_info)
        for artist in song_info['artists']:
            artists = f"{artists}{artist},"
        text = f"{artists[:-1]} - {song_info['title']}"
        return text

    @commands.command(help = '''shows current queue''')
    async def queue(self,ctx):
        embedmaker = self.bot.get_cog("EmbedMaker")
        current_server = ctx.message.guild
        if len(self.queue[current_server]) == 0:
            embed = await embedmaker.embed(ctx,description = f"I can't seem to find a person denser than {ctx.message.author.mention}")
        else:
            text = '''__Now Playing:__\n'''
            first_index = 0
            if self.queue[current_server][0] == "filler":
                first_index = 1
            song = self.queue[current_server][first_index]
            song_name = await self.format_song(song)
            text = f"{text}[{song_name}]({song['url']}) | `{song['duration']}`\n"
            text = f"{text}__Queue__\n"
            for index in range(first_index+1,len(self.queue[current_server])):
                song = self.queue[current_server][index]
                song_name = await self.format_song(song)
                text = f"{text}[{song_name}]({song['url']}) | `{song['duration']}`\n"
            embed = await embedmaker.embed(ctx,title = "Queue",description = text)
        await ctx.send(embed = embed)
        








        


def setup(bot):
    bot.add_cog(Music(bot))