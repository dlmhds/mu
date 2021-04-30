from discord.ext import commands

class Song(commands.Cog):
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

def setup(bot):
    bot.add_cog(Song(bot))