"""
The collaborative filtering portion of the system.
Should always be used with databases.database
"""

import math

import databases.database as databases
import math

class CollaborativeFilter:
    """
    A Collaborative Filtering algorithm/object meant to be heavily optimized for speed
    """

    def __init__(self, name, path, table, debug=False, cache=True):
        """
        Initilialies the collaborative filter with the values

        Arguments:
            name  -> the name of the database file
            path  -> the path to the database file
            table -> the name of the table in the database file
            debug -> activates debug mode, providing additional outputs and information about what is happening
            cache -> used for testing, to compare between the caches being used and a normal, cache free version
                        both for benchmarking and for error checking
        """


        self.name = name
        self.path = path
        self.table = table
        self.debug = debug
        self.cache = cache
        self.db = databases.Database(name, table, path)

        #implemented as map(user->map(item->opinion))
        #opinions can be None or 1-5
        self.opinions = {}

        #implemented as map(user1->map(user2->tuple(rss(u1), rss(u2), multSum(u1, u2))))
        #rss(u) is root sum squared
        #multSum(u1, u2) is sum(u1[item]*u2[item] for item in sharedItems)
        self.similarities = {}

        #implemented as map(user1->map(user2->tuple(sum(simil*r for user in users), sum(simil for user in users))))
        self.calculated = {}

    def fetchOpinion(self, user, item):
        """
        """
        pass


    def predictOpinion(self, user, item):
        """
        """
        pass

    def changeOpinion(self, user, item, opinion):
        """
        """
        pass