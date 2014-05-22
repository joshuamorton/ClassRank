"""
The collaborative filtering portion of the system.
Should always be used with databases.database
"""


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
        self.db = databases.Database(self.name, self.table, self.path)
        self.users = {} #the set of users in the database

        #implemented as map(user->map(item->opinion))
        #opinions can be None or 1-5
        self.opinions = {}

        #implemented as map(user1->map(user2->tuple(rss(u1), rss(u2), multSum(u1, u2))))
        #rss(u) is root sum squared
        #multSum(u1, u2) is sum(u1[item]*u2[item] for item in sharedItems)
        self.similarities = {}

        #implemented as map(user1->map(item->tuple(sum(simil*opinions[user][item] for user in users), sum(simil for user in users))))
        self.calculated = {}

    def fetchOpinion(self, user, item):
        """
        Directly fetches an opinion from the database
        
        Arguments:
            user -> the user who has an opinion
            item -> the item of which they have an opinion

        return a value representing the user's opinion of the item, or none if the user has no opinion
        """
        return db.currentOpinion(user, item)


    def predictOpinion(self, user, item):
        """
        Calculates a user's opinion of an item based on the collaborative filtering algorithm.  Uses caches if possible
            and falls back to the long method of calculation if necessary

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion
        """
        if (self.cache == True):
            if user in self.calculated:
                if item in self.calculated[user]:
                    return _ratingFromCalculated(*self.calculated[user][item])
                else: #if item not in self.calculated[user]
                    self.calculated[user][item] = self._calculateWeights(user, item)
                    return _ratingFromCalculated(*self.calculated[user][item])
            else: #if user note in self.calculated
                self.calculated[user] = {}
                self.calculated[user][item] = self._calculateWeights(user, item)
        else: #if calculation is forced
            pass #for now


    def _ratingFromCalculated(weightedRatings, sumSimilarities):
        """
        Uses the values stored in self.calculated to find the final rating for a user

        Arguments:
            weightedRatings -> The first value in self.calulated it is represented by
                               sum(simil(u, u') * opinions[u'][i] for u' in Users)

            sumSimilarities -> The second value in self.calculated, which represents
                               sum(simil(u, u') for u' in Users)

        returns r[u][i], the rating that user u would give to item i
        """

        #forces floating point division
        return float(weightedRatings) / sumSimilarities


    def _calculateWeights(self, user, item):
        """
        returns a tuple (self._ratingTop(user, item), self._ratingBottom(user, item))
        """
        
        #create the users and items sets
        users = {person[0] for person in self.dbViewer.users()} - {user}

        #use those sets to seperately calculate the top and bottom values for the final rating
        return (self._ratingTop(user, item, users), self._ratingBottom(user, item, users))


    def _ratingTop(self, user, item, users):
        """
        Returns the top portion of the calculated opinion

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion
        """

        #get the items shared by both users
        return sum(self._similarity(user, other) * self._opinion(other, item) for other in users)


    def _ratingBottom(self, user, item, users):
        """

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion
        """
        return sum(self._similarity(user, other) for other in users)


    def _similarity(self, user, other):
        """
        Arguments:
            user  -> the user whose opinion is being calculated
            other -> the other user to whom the user is being compared

        """
        
        if (self.cache == True):
            if user in self.similarities:
                if other in self.similarities[user]:
                    return self._calculateSimilarity(*self.similarities[user][other])
                else:
                    self.similarities[user][other] = self._setSimilarities(user, other)
                    return self._calculateSimilarity(*self.similarities[user][other])
            else:
                self.similarities[user] = {}
                self.similarities[user][other] = self._setSimilarities(user, other)
                return self._calculateSimilarity(*self.similarities[user][other])
        else:
            pass #for now


    def _calculateSimilarity(self, rssUser, rssOther, multSum):
        """
        calculates the similarity between users based on the rss and multSum values
        """

        return multSum / (rssUser * rssOther)
        

    def _setSimilarities(user, other):
        """
        """
        pass


    def _opinion(self, user, item):
        """
        gets the opinion a user has about an item from the database
        
        Arguments:
            user -> a user whose opinion we want
            item -> the item for which we want their opinion
    
        """
        if user in self.opinions:
            if item in self.opinions[user]:
                return self.opinons[user][item]
            else:
                self.opinions[user][item] = db.currentOpinion(user, item) or 0
                return self.opinions[user][item]
        else:
            self.opinions[user] = {}
            self.opinons[user][item] = db.currentOpinion(user, item) or 0
            return self.opinions[user][item]


    def changeOpinion(self, user, item, opinion):
        """

        """
        pass

    
if __name__=="__main__":
    cf = CollaborativeFilter("database.db", "databases/data", "main")