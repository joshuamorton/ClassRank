import sqlite3
import os.path
import ast


class Database:

    """
    a wrapper api for the wrapper apis to make my life easier
    assumes all databases are simply key-> value stores where
        key - the username/other identifying string of a user
        value - an array of integers from 1-5 representing how much people like/dislike things or 0 representing null
    Simplifying assumptions:
        Items cannot be removed from the database (although users can)
        New items will always be appended to the end of the database

    This also means that for future database migrations/changes/whatever, this is all that will need to change.

    This is currently insecure and vulnerable to SQL injection via a an annoying user, I'll fix that
    """



    def __init__(self, name, table, size):

        """
        var name - the filename of the database to be connected to
        var size - the number of things that users can like or dislike
        """

        self.field = "array"
        self.username = "username"
        self.databaseFolder = "data"
        self.name = name
        self.table = table
        self.db = sqlite3.connect(os.path.join(self.databaseFolder,self.name))
        self.cursor = self.db.cursor()
        self.size = size


    def addItem(self):

        """
        Adds an item to the database by increasing the size variable
        """

        self.size += 1


    def addUser(self, user):

        """
        adds a user to the database, by initializing them with an array of 0s
        """

        #TODO: check to see a user of the same name is in the database first
        values = [0 for x in xrange(self.size)]
        self.cursor.execute("INSERT INTO {table} VALUES ('{user}', '{values}')".format(table = self.table, user = user, values = values, username = self.username))
        self.db.commit()


    def delUser(self, user):

        """
        removes a user from the database
        """

        self.cursor.execute("DELETE FROM {table} WHERE {username} ='{user}'".format(table = self.table, user = user, username = self.username))
        self.db.commit()


    def getUser(self, user):

        """
        returns the array of values (converted to python-readable data) for a given user
        """

        self.cursor.execute("SELECT * FROM {table} WHERE {username} = '{user}'".format(table = self.table, user = user, username = self.username))
        values = self.cursor.fetchone()[1]
        values = self._padValues(values)
        return values

    def setUser(self, user, values):
        """
        """
        self.cursor.execute("UPDATE {table} SET {thing}='{values}' WHERE {username} = '{user}'".format(table = self.table, user = user, username = self.username, thing = self.field, values = values))
        self.db.commit()


        """
        """
    def updateItem(self, user, item, value):
        values = getUser(user)
        values[item] = value
        setUser(user, values)


    #helper fucntions
    def _padValues(self, values):

        """
        Pads the array from a user into a longer array, also turns the string array into an array, so that's important.
        var values - 
        return vals, the padded, list-form version of the information contained in the database
        """

        vals = ast.literal_eval(values)
        if len(vals) < self.size:
            vals += [0 for x in xrange(self.size-len(vals))]
        return vals


class Viewer:
    """
    Basically a Database object, except it can't edit existing databases (without someone doing...things)
    """

    def __init__(self, name, table, size):

        """
        var name - the filename of the database to be connected to
        var table - 
        var size - the number of things that users can like or dislike
        """

        self.field = "array"
        self.username = "username"
        self.databaseFolder = "data"
        self.name = name
        self.table = table
        self.db = sqlite3.connect(os.path.join(self.databaseFolder,self.name))
        self.cursor = self.db.cursor()
        self.size = size

    def getUser(self, user):

        """
        returns the array of values (converted to python-readable data) for a given user
        """

        self.cursor.execute("SELECT * FROM {table} WHERE {username} = '{user}'".format(table = self.table, user = user, username = self.username))
        values = self.cursor.fetchone()[1]
        values = self._padValues(values)
        return values


if __name__ == "__main__":
    thing = Database("persistent.db", "opinions", 9)
    thing.addUser("me")

