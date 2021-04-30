from ytmusicapi import YTMusic 
import json
from discord.ext import commands

class GuessGame(commands.Cog):
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
        self.rounds_played = 0
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
        guess = list(guess.lower().split(" "))
        print(f"guess: {guess}")
        correct = True
        for word in guess:
            print(word)
            if word not in self.matches:
                correct = False
                points = 0
        if correct:
            points = int(len(guess)*10/len(self.matches))
            self.scoreboard.add_points(player,points)

        return points

    #returns top 10 players
    def get_leaderboard(self):
        if self.scoreboard.size() > 10:
            return self.scoreboard.get_leaderboard(10)
        else: 
            return self.scoreboard.get_leaderboard()

def setup(bot):
    bot.add_cog(GuessGame(bot))