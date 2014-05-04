"""
The collaborative filtering portion of the system.
Should always eb used with databases
heavily modified version of the code here:
    https://github.com/uenowataru/CollaborativeFiltering/blob/master/CollaborativeFiltering.py
"""

import databases.Database as databases
import math

class CollaborativeFilter:
    """
    A Collaborative Filtering algorithm/object meant to be heavily optimized for speedx
    """

    def __init__(self, database, table, folder):
        """
        """
        self.dbViewer = databases.Viewer(database, table, folder)
        self.db = databases.Database(database, table, folder)
        
        #cache is a dictionary in the form {username:dictionary{item:value}}
        #in short, a limited version of the larger table
        #it might behove me to update the weights to its own object that keeps track of active users and stores information
        #only relevant to them, periodically purging itsself.
        self.cache = {}

    def calculateOpinion(self, user, item):
        """
        """
        users = {person[0] for person in self.dbViewer.users()} - {user}
        print users
        if user in self.cache:
            return cache[user][item] if item in cache[user] else None
        else:
            pass
            #users = [_calculateSimilarities(user, other) for other in users]

    def _calculateSimilarities(self, user, other):
        """
        Calculates the similarity between to users via the fitness function cos(vec(x), vec(y)):
        (sum[for i in the list of Items shared by users x and y](rating of x for i * rating of y for i))/((rss of rating(i) for i by x) * (rss of rating(i) for i by y)
        where rss is the root sum squared computed by sqrt(sum[for i in the list of Items rated by user u](rating of i by u)**2)
        see cos.png.
        """
        





if __name__ == "__main__":
    assert 258 ==  258
    #do more
    x = CollaborativeFilter("database.db", "main", "databases/data")
    assert x.dbViewer.currentOpinions("them") == x.db.currentOpinions("them")
    print x.dbViewer.currentOpinions("them")
    x.calculateOpinion("them",5)