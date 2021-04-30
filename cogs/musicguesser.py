from discord.ext import commands, tasks
import discord
import youtube_dl
import json
from ytmusicapi import YTMusic
import datetime
import random
import os
import asyncio

#TODO, get rid of FFMPEG and use Lavalink

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
        self.game_runner.start()

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

class MusicGuesser(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        with open("data/score.json",'r') as f:
            jsondump = json.load(f)
        self.scores = jsondump #stores the cumulative score of a server
        with open("data/playlist_ids.json", 'r') as f:
            jsondump = json.load(f)
        self.playlist_ids = jsondump
        self.ytmusic = YTMusic()
        self.pop_playlist = self.ytmusic.get_playlist(self.playlist_ids['pop'],300)['tracks']
        self.local_scores = {} #stores the score for each game
        self.guess_data = {
            #"server": {"channelid":"","song playing":"","played":""}
        }




    async def get_playlist(self,playlist_id):
        playlist = self.ytmusic.get_playlist(playlist_id,300)['tracks']
        return playlist

    #start and duration are in seconds
    async def shorten_file(self,url,start,duration):
        #get the file
        filename_long = await YTDLSource.from_url(url,loop = self.bot.loop)
        #shorten the file
        start_formatted = str(datetime.timedelta(seconds = start))
        duration_formatted = str(datetime.timedelta(seconds = duration))
        file_path = f"{os.path.abspath(os.getcwd())}\\{filename_long}"
        print(file_path)
        filename =  f"{random.randrange(0,10000000)}-{random.randrange(0,10000000)}.m4a"
        cmd = f'''ffmpeg -ss {start_formatted} -i "{file_path}" -vn -c copy -t {duration_formatted} {filename}'''
        print(cmd)
        os.system(cmd)
        await asyncio.sleep(3)
        os.remove(filename_long)
        return filename

    @commands.Cog.listener()
    async def on_message(self,message):
        print(message.content)
        print(message.channel.id)
        print(self.guess_data)
        if message.author == self.bot.user:
            return
        #makes sure there is a guess game running in the channel
        if message.guild in self.guess_data and message.channel.id == self.guess_data[message.guild]['channelid']:
            song = self.guess_data[message.guild]['song playing']
            song.split()
            guess = message.content
            guess.split()
            match = True
            print(f"song: {song}")
            print(f"guess: {guess}")
            for word in guess:
                if word not in song:
                    match = False
            if match:
                points = int((len(guess)/len(song))*10)
                embedmaker = self.bot.get_cog("EmbedMaker")
                ctx = await self.bot.get_context(message)
                text = f'''{message.author.mention} has **correctly** guessed {self.guess_data[message.guild]['song playing']}
                            and earned {points} points. guess: {guess}'''
                embed = await embedmaker.embed(ctx,description = text)
                await ctx.send(embed = embed)
                self.guess_data[message.guild]['played'] += 1
                self.guess_data[message.guild]['song playing'] = None
                #stop playing


    #this loops manages the guessing game and advances the songs
    @tasks.loop(seconds = 1)
    async def game_runner(self):
        for server in self.guess_data:
            #bot is kicked from vc
            if server.voice_client is None:
                self.guess_data.pop(server)
            #the song has been guessed or expired
            elif not server.voice_client.is_playing():
                #song was not guessed and time is up
                if self.guess_data[server]['song playing'] != None:
                    text = f'''**Times Up!** The song was {self.guess_data[server]['song playing']}'''
                    embedmaker = self.bot.get_cog("EmbedMaker")
                    embed = await embedmaker.embed(ctx,description = text)
                    await ctx.send(embed = embed)
                #increment played songs by 1
                self.guess_data[server]['played'] += 1

                if self.guess_data[server]['played'] == 10:
                    self.guess_data.pop(server)
                    #print leaderboard/winner
                else:
                    next_song = await self.play_random_song(server)
                    music = self.bot.get_cog("Music")
                    self.guess_data[server]["song playing"] = await music.format_song(next_song)

    async def play_random_song(self,server):
        next_song = self.pop_playlist[random.randrange(0,len(self.pop_playlist))]
        m, s = next_song['duration'].split(':')
        song_duration = int(m) * 60 + int(s)
        #how long to play the song
        play_duration = 30
        start = random.randrange(20,song_duration - play_duration)
        filename = await self.shorten_file(f"http://www.youtube.com/watch?v={next_song['videoId']}",start,play_duration)
        #plays song
        music = self.bot.get_cog("Music")
        await music.play_song(next_song,server,filename)
        return next_song

    #this command creates the guessing game
    @commands.command(help = '''start guessing game''')
    async def guess(self,ctx):
        #later add in option to pick music genres

        music = self.bot.get_cog("Music")
        embedmaker = self.bot.get_cog("EmbedMaker")
        voice = ctx.message.guild.voice_client
        if voice is None or not voice.is_connected():
            await music.join(ctx)
        if ctx.message.author.voice:
            #plays the first random song
            server = ctx.message.guild
            next_song = await self.play_random_song(server)
            
            #records that a guessing game is running
            self.guess_data[server] = {}
            self.guess_data[server]["song playing"] = await music.format_song(next_song)
            self.guess_data[server]["played"] = 0
            self.guess_data[server]["channelid"] = ctx.message.channel.id

            embed = await embedmaker.embed(ctx,description = "Started guessing game in the pop genre for 10 songs")
        else:
            embed = await embedmaker.embed(ctx,description = "Unicorns over the rainbow")
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(MusicGuesser(bot))