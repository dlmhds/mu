from discord.ext import commands

class ScoreBoard(commands.Cog):
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

def setup(bot):
    bot.add_cog(ScoreBoard(bot))