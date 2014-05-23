"""
The collaborative filtering portion of the system.
"""


import databases.database as databases
import math
import sys

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

    def fetchOpinion(self, user, item): #done
        """
        Directly fetches an opinion from the database
        
        Arguments:
            user -> the user who has an opinion
            item -> the item of which they have an opinion

        return a value representing the user's opinion of the item, or none if the user has no opinion
        """
        return self.db.currentOpinion(user, item)


    def predictOpinion(self, user, item): #done except for the cache disabled (needs refactoring) needs docs
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
                    return self._ratingFromCalculated(*self.calculated[user][item])
                else: #if item not in self.calculated[user]
                    self.calculated[user][item] = self._calculateWeights(user, item)
                    return self._ratingFromCalculated(*self.calculated[user][item])
            else: #if user note in self.calculated
                self.calculated[user] = {}
                self.calculated[user][item] = self._calculateWeights(user, item)
                return self._ratingFromCalculated(*self.calculated[user][item])
        else: #if calculation is forced
            pass #for now
            #return self._directCalculateRating(user, item)


    def _ratingFromCalculated(self, weightedRatings, sumSimilarities): #done
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


    def _calculateWeights(self, user, item): #done needs docs
        """
        returns a tuple (self._ratingTop(user, item), self._ratingBottom(user, item))
        """
        
        #create the users and items sets
        users = {person[0] for person in self.db.users()} - {user}

        #use those sets to seperately calculate the top and bottom values for the final rating
        return (self._ratingTop(user, item, users), self._ratingBottom(user, item, users)) 


    def _ratingTop(self, user, item, users): #done
        """
        Calculates the top portion of the fraction that a user would have for an item based on other users

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion

        Returns the top portion of the calculated opinion
        """

        #get the items shared by both users
        return sum(self._similarity(user, other) * self._opinion(other, item) for other in users)


    def _ratingBottom(self, user, item, users): #done, needs docs
        """

        Arguments:
            user -> the user whose opinion is to be calculated
            item -> the item of which the user has an unknown opinion
        """
        return sum(self._similarity(user, other) for other in users)


    def _similarity(self, user, other): #done (needs refactoring) needs docs
        """
        Arguments:
            user  -> the user whose opinion is being calculated
            other -> the other user to whom the user is being compared

        """
        
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


    def _calculateSimilarity(self, rssUser, rssOther, multSum): #done needs docs
        """
        calculates the similarity between users based on the rss and multSum values
        """

        return multSum / (rssUser * rssOther)
        

    def _setSimilarities(self, user, other): #done
        """
        seperately calculate rss(user), rss(other), and multsum(user, other) and return them
        """

        items = items = [column[0] for column in self.db.items()]
        sharedItems = {item for item in items if self._opinion(user, item) is not 0} & {item for item in items if self._opinion(other, item) is not 0}
        userRss = self._rss(user, sharedItems)
        otherRss = self._rss(other, sharedItems)
        multsum = self._multSum(user, other, sharedItems)
        return (userRss, otherRss, multsum)

        
    def _rss(self, user, shared): #done, needs docs
        """
        """
        return math.sqrt(sum(self._opinion(user, item) ** 2 for item in shared))


    def _multSum(self, user, other, shared): #done, needs docs
        """
        """
        return sum(self._opinion(user, item) * self._opinion(other, item) for item in shared)


    def _opinion(self, user, item): #done
        """
        gets the opinion a user has about an item from the database
        
        Arguments:
            user -> a user whose opinion we want
            item -> the item for which we want their opinion
    
        """
        if user in self.opinions:
            if item in self.opinions[user]:
                return self.opinions[user][item]
            else:
                self.opinions[user][item] = self.db.currentOpinion(user, item) or 0
                return self.opinions[user][item]
        else:
            self.opinions[user] = {}
            self.opinions[user][item] = self.db.currentOpinion(user, item) or 0
            return self.opinions[user][item]


    def changeOpinion(self, user, item, opinion): #TODO
        """

        """
        pass

    
if __name__=="__main__":
    cf = CollaborativeFilter("database.db", "databases/data", "main")
    users = ["one", "two", "three", "four"]
    classes = ["CS1331", "CS1332", "CS1333", "CS1334"]
    for user in users:
        for clazz in classes:
            sys.stdout.write(user+" "+clazz+" - "+str(cf.predictOpinion(user, clazz))+"\n")