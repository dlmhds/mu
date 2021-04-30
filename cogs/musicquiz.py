import wavelink
import discord
from discord.ext import commands
import json
from ytmusicapi import YTMusic 
import random

class Song():
    def __init__(self,title: str,artists: list,duration: str,yt_id: str):
        self.title = title
        self.artists = artists
        self.duration = duration
        self.url = f"http://www.youtube.com/watch?v={yt_id}"
        self.formatted = self.format()

    def format(self):
        a = ""
        for artist in self.artists:
            if artist not in self.title:
                a = f"{a}, {artist}"
        return f"{a[1:]} - {self.title}"

class Queue():
    def __init__(self):
        self.queue = []
        self.index = 0

        #None - no loop
        #One - loop song
        #All - loop queue
        self.loop = None

    #removes from queue
    def pop(self,pos):
        self.queue.pop(pos)

    #returns item at pos in queue
    def at(self,pos):
        return self.queue[pos]

    #returns size of queue
    def size(self):
        return len(self.queue)

    #appends item to end of queue
    def append(self,item):
        self.queue.append(item)

    #returns the next in queue
    #returns None if at end of queue
    def next(self):
        if self.loop == None:
            if self.index < self.size() - 1:
                self.index += 1
                return self.at(index)
            else:
                return None
        if self.loop == "One":
            return self.at(index)
        if self.loop == "All":
            if self.index < self.size() - 1:
                self.index += 1
            else:
                #index = size - 1
                self.index = 0
            return self.at(index)

    #returns current
    def current(self):
        return self.at(self.index)

    #returns random
    def random(self):
        return self.at(random.randrange(0,self.size()))




class ScoreBoard():
    def __init__(self):
        self.players = []
        self.scores = {}

    def add_player(self,player):
        self.players.append(player)
        self.scores[player] = 0

    def size(self):
        return len(self.players)

    def add_points(self,player,points):
        if player not in self.players:
            self.add_player(player)
        self.scores[player] += points

    def get_points(self,player):
        return self.scores[player]

    #high first lower later
    def sort_scores(self):
        self.scores = dict(sorted(self.scores.items(),key = lambda item: item[1],reverse = True))

    #highest point comes first
    def get_leaderboard(self,length = None):
        if length == None:
            length = len(self.players)
        leaderboard = [] #[[player,score],...]
        self.sort_scores()
        i = 1
        for x in self.scores:
            if i > length:
                break
            leaderboard.append([x,self.scores[x]])
            i += 1
        return leaderboard

class GuessGame():
    def __init__(self,server=None,channel_id=None,rounds=None,genre=None,playlist_id = None):
        self.bot = bot
        self.server = server
        self.channel_id = channel_id
        self.rounds = rounds
        self.genre = genre
        self.playlist = self.get_playlist(genre,playlist_id)
        self.rounds_played = 0
        self.scoreboard = ScoreBoard()
        self.music_played = []
        self.currently_playing = None
        self.current_title = None
        self.matches = None
        self.in_game = False
        self.guessed = False

    def set_settings(self,server=False,channel_id=False,rounds=False,genre=False,playlist_id=False):
        if server: 
            self.server = server
        if channel_id: 
            self.channel_id = channel_id
        if rounds: 
            self.rounds = rounds
        if genre: 
            self.genre = genre
        if playlist_id: 
            self.playlist = self.get_playlist(genre,playlist_id)
        if genre and self.playlist == None:
            self.playlist = self.get_playlist(genre,None)

    def start_game(self):
        self.guessed = False
        self.rounds_played = 0
        self.music_played = []
        self.in_game = True

    def get_playlist(self,genre,playlist_id):
        if playlist_id == None and genre == None:
            return None
        ytmusic = YTMusic()
        if playlist_id == None:
            with open("data/playlist_ids.json",'r') as f:
                jsondump = json.load(f)
            playlist_id = jsondump[genre]
            playlist_data = ytmusic.get_playlist(playlist_id,1000)['tracks']
        else:
            playlist_data = ytmusic.get_playlist(playlist_id,1000)['tracks']
        playlist = Queue()
        for s in playlist_data:
            title = s['title']
            duration = s['duration']
            yt_id = s['videoId']
            artists = []
            for artist in s['artists']:
                artists.append(artist['name'])
            song = Song(title = title, duration = duration, artists = artists, yt_id = yt_id)
            playlist.append(song)
        return playlist

    def remove_clutter(self,string):
        clutter = ['(',')','{','}','-','[',']','&']
        for x in clutter:
            string = string.replace(x," ")
        return string

    #returns next song to be played
    def next(self):
        self.guessed = False
        self.music_played.append(self.currently_playing)
        self.rounds_played += 1
        #see if games has ended
        if self.rounds_played >= self.rounds:
            self.in_game = False
            return None
        song = None
        while song == None or song in self.music_played:
            song = self.playlist.random()

        self.currently_playing = song
        self.current_title = song.formatted
        print(self.remove_clutter(self.current_title))
        self.matches = list(filter(lambda x: x != '',list(self.remove_clutter(self.current_title).lower().split(" "))))
        print(self.matches)
        return self.currently_playing

    #returns points 
    def guess(self,player,guess: str):
        if self.guessed:
            points = 0
        else:
            guess = list(guess.lower().split(" "))
            print(f"guess: {guess}")
            correct = True
            for word in guess:
                print(word)
                if word not in self.matches:
                    correct = False
                    points = 0
            if correct:
                self.guessed = True
                points = int(len(guess)*10/len(self.matches))
                self.scoreboard.add_points(player,points)

        return points

    #returns top 10 players
    def get_leaderboard(self):
        #[[player,score],...]
        if self.scoreboard.size() > 10:
            return self.scoreboard.get_leaderboard(10)
        else: 
            return self.scoreboard.get_leaderboard()



class AlreadyConnected(commands.CommandError): pass

class NoVoiceChannelGiven(commands.CommandError): pass

class Player(wavelink.Player):
    def __init__(self,*args,**kwargs):
        super.__init__(*args,**kwargs)
        self.guessgame = GuessGame()
        self.play_duration = 30

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

    #return whether a guessing game is running
    def in_game(self):
        return self.guessgame.in_game

    async def guess(self,player,guess: str):
        points = self.guessgame.guess(player,guess)
        if points > 0:
            #they guessed correctly
            #stop playing current song
            self.stop()
        return points

    async def next(self):
        #self destruct if not in game
        if not self.in_game():
            await self.teardown()
            return False

        song = self.guessgame.next()


        if song == None:
            #There is no next song
            return False

        track = await self.wavelink.get_tracks(song.url)

        m, s = song.duration.split(":")
        song_duration = int(m) * 60 + int(s)

        start = random.randrange(20,song_duration - self.play_duration)
        end = start + self.play_duration

        await self.play(track,start = start, end = end)
        return True


class MusicQuiz(commands.Cog,wavelink.WavelinkMixin):
    def __init__(self,bot):
        self.bot = bot
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.player_directory = {}
        self.bot.loop.create_task(self.start_nodes())


    async def start_nodes(self):
        await self.bot.wait_until_ready()
        await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                              port=2333,
                                              rest_uri='http://127.0.0.1:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='us_central')


    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    async def make_leaderboard(self,leaderboard):
         embedmaker = self.bot.get_cog("EmbedMaker")
         text = ''
         place = 1
         for person in leaderboard:
            text = f"{text}\n`{place}. {person[1]}  |  <@{person[0]}>"
            place += 1
         embed = embedmaker(description = text)
         return embed


    @wavelink.WavelinkMixin.listener("on_track_end")
    async def on_play_stop(self,node,payload):
        
        embedmaker = self.bot.get_cog("EmbedMaker")
        channel = await self.bot.get_channel(payload.player.guessgame.channel_id)
        guessgame = payload.player.guessgame
        #checks to see if no one guessed
        if not guessgame.guessed:
            embed = await embedmaker.embed(description = f'''**Times Up!** The song is `{guessgame.current_title}`''')

            await channel.send(embed = embed)

        #if there is no next song
        if not await payload.player.next():
            #retrieve leaderboard
            leaderboard = payload.player.guessgame.get_leaderboard()
            embed = await self.make_leaderboard(leaderboard)
            #destroy player
            payload.player.teardown()
        else:
            embed = await embedmaker.embed(description = f'**Playing {guessgame.played + 1}/{guessgame.rounds}**')
        await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message(self,message):
        player = self.get_player(message.guild)

        if message.channel.id != player.guessgame.channel_id:
            #message not sent in same channel as the music quiz, ignore
            return

        if message.author.voice.channel == None:
            #author is not in voice channel, ignore
            return

        points = await player.guess(message.author.id,message.content)
        if points > 0:
            embedmaker = self.bot.get_cog("EmbedMaker")
            embed = await embedmaker.embed(f'''The song is `{player.guessgame.current_title}`\n
                                                {message.author.mention} guessed {message.content}
                                                and earned **{points} pts**''')

            channel = await self.bot.get_channel(message.channel.id)
            await channel.send(embed = embed)

    @commands.command(help = ''' starts musiz quiz''')
    async def quiz(self,ctx,rounds = 10):
        embedmaker = self.bot.get_cog("EmbedMaker")
        player = self.get_player(ctx)
        channel = await player.connect(ctx,channel)

        embed = await embedmaker.embed(ctx,description = f"Successfully joined *{ctx.author.voice.channel}*")
        await ctx.send(embed=embed)
        embedmaker = self.bot.get_cog("EmbedMaker")

def setup(bot):
    bot.add_cog(MusicQuiz(bot))