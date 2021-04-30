from ytmusicapi import YTMusic 
import random
import json

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
    def __init__(self,server,channel_id,rounds,genre,playlist_id = None):
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

    def get_playlist(self,genre,playlist_id):
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

    #returns whether guess is sucessful or not
    def guess(self,player,guess: str):
        guess = list(guess.lower().split(" "))
        print(f"guess: {guess}")
        correct = True
        for word in guess:
            print(word)
            if word not in self.matches:
                correct = False
        if correct:
            points = int(len(guess)*10/len(self.matches))
            self.scoreboard.add_points(player,points)

        return correct

    #returns top 10 players
    def get_leaderboard(self):
        if self.scoreboard.size() > 10:
            return self.scoreboard.get_leaderboard(10)
        else: 
            return self.scoreboard.get_leaderboard()

#class MusicPlayer():

