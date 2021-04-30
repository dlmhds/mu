import random
from discord.exe import commands

class Queue(commands.Cog):
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

def setup(bot):
    bot.add_cog(Queue(bot))