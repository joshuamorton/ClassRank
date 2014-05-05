"""
The collaborative filtering portion of the system.
Should always eb used with databases
heavily modified version of the code here:
    https://github.com/uenowataru/CollaborativeFiltering/blob/master/CollaborativeFiltering.py
"""

import math

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

        #similarities is a dictionary in the form {username:dictionary{username:(similarity between user x and y)}}
        #also might behove to rewrite this as an object that clears itsself overtime and does stuff based on active users
        self.similarities = {}

        #opinions is a dictionary in the form {username:dictionary{item:(predicted opinion of item by user)}}
        self.opinions = {}

    def calculateOpinion(self, user, item):
        """
        """
        if user in self.opinions:
            if item in self.opinions[user]:
                return self.opinions[user][item] if item in self.opinions[user] else None
            else:
                users = {person[0] for person in self.dbViewer.users()} - {user}
                self.opinions[user][item] = self._k(user, users) * sum(self._calculateSimilarities(user, other) * self._fetchOpinion(other, item) for other in users)
                return self.opinions[user][item]
        else:
            users = {person[0] for person in self.dbViewer.users()} - {user}
            self.opinions[user] = {}
            self.opinions[user][item] = self._k(user, users) * sum(self._calculateSimilarities(user, other) * self._fetchOpinion(other, item) for other in users)
            return self.opinions[user][item]

    def _k(self, user, users):
        """
        """
        return 1.0 / sum(self._calculateSimilarities(user, other) for other in users)

    def _calculateSimilarities(self, user, other):
        """
        Calculates the similarity between to users via the fitness function cos(vec(x), vec(y)):
        (sum[for i in the list of Items shared by users x and y](rating of x for i * rating of y for i))/((rss of rating(i) for i by x) * (rss of rating(i) for i by y)
        where rss is the root sum squared computed by sqrt(sum[for i in the list of Items rated by user u](rating of i by u)**2)
        see cos.png
        """
        if user in self.similarities:
            if other in self.similarities[user]:
                return self.similarities[user][other]
            else:
                items = [column[0] for column in self.dbViewer.items()]
                sharedItems = {item for item in items if self.dbViewer.currentOpinion(user,item) is not None} & {item for item in items if self.dbViewer.currentOpinion(other,item) is not None}
                opinionSum = sum(self._fetchOpinion(user, item) * self._fetchOpinion(other, item) for item in sharedItems)
                self.similarities[user][other] = opinionSum / (self._rss(user, sharedItems) * self._rss(other, sharedItems))
                return self.similarities[user][other]
        else:
            self.similarities[user] = {}
            items = [column[0] for column in self.dbViewer.items()]
            sharedItems = {item for item in items if self.dbViewer.currentOpinion(user,item) is not None} & {item for item in items if self.dbViewer.currentOpinion(other,item) is not None}
            opinionSum = sum(self._fetchOpinion(user, item) * self._fetchOpinion(other, item) for item in sharedItems)
            self.similarities[user][other] = opinionSum / (self._rss(user, sharedItems) * self._rss(other, sharedItems))
            return self.similarities[user][other]

    def _rss(self, user, shared):
        """
        """
        return math.sqrt(sum(self._fetchOpinion(user, item) ** 2 for item in shared))

    def _fetchOpinion(self, user, item):
        """
        """
        if user in self.cache:
            return self.cache[user][item]
        else:
            items = (column[0] for column in self.dbViewer.items())
            self.cache[user] = {item: self.dbViewer.currentOpinion(user, item) for item in items}
            return self.cache[user][item]
        





if __name__ == "__main__":
    assert 1 == 1
    #do more
    x = CollaborativeFilter("database.db", "main", "databases/data")
    print x.calculateOpinion("two", "CS1335")
    print x.calculateOpinion("three", "CS1334")
