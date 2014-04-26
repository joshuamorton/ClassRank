import sqlite3
import os.path


class Database:
    """
    a wrapper api for the wrapper apis to make my life easier
    assumes all databases are simply key-> value stores where
        key - the username/other identifying string of a user
        value - an array of integers from 0-5 representing how much people like/dislike things
    Simplifying assumptions:
        Items cannot be removed from the database (although users can)
        New items will always be appended to the end of the database

    This also means that for future database migrations/changes/whatever, this is all that will need to change.
    """


    """
    var name - the filename of the database to be connected to
    var size - the number of things that users can like or dislike
    """
    def __init__(self, name, table, size):
        self.databaseFolder = "data"
        self.name = name
        self.table = table
        self.db = sqlite3.connect(os.path.join(self.databaseFolder,self.name))
        self.cursor = self.db.cursor()
        self.size = size

    """
    Adds an item to the database
    """
    def addItem(self):
        self.size += 1

    def addUser(self, user):
        values = [0 for x in xrange(self.size)]
        self.cursor.execute("INSERT INTO {table} VALUES ('{user}', '{values}')".format(table = self.table, user = user, values = values))
        self.db.commit()

    def delUser(self, user):
        pass

    def getUser(self, user):
        pass
        
    def updateItem(self, user, item):
        pass

    #helpers
    def padUser(self, user):
        pass

if __name__ == "__main__":
    thing = Database("persistent.db", "opinions", 9)
    thing.addUser("me")
    
