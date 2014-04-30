"""
"""

import sqlite3
import os.path


class Database(object):
    """
    A database wrapper for a table that has many rows but few columns
    Tables:
        username -> unique key, [x columns representing opinions on items]
    """

    
    def __init__(self, name="database.db", table="main", folder="data"):
        """
        Initialize the database object
        keyword arguments:
            name - the name of the database file
            table - the name of the table within the databse

        the name and table arguments are given defaults, and should be set in a configuration file

        instance data:
            databaseFolder - the folder where the database file is
            usernameField - the text name of the field where the user's username is held in the table
            uniqueID - the text name of the field where the id for each user is held in the table
            name - the name of the database file
            table - the name of the table used by this object
            path - the absolute path to the database file
            ----the following are initialized in __init__, although not clearly----
            db - the sqlite3 database object (used for connections, commits, and closes)
            cursor - the sqlite3 cursor object (used for executes)
            columnInfo - list<tuple<column name, data type>> for each column in the database
        """

        #initialize values
        self.databaseFolder = folder
        self.usernameField = "username"
        self.uniqueID = "id"
        self.name = name
        self.table = table
        self.path = os.path.join(self.databaseFolder,self.name)

        #check to see if database exists, if yes, connect to it, if no, create and then connect to it
        if (os.path.isfile(self.path)):
            self._connect()
        else:
            self._create()
            self._connect()

        self.tableLength = len(self.columnInfo) - 2



    def _create(self):
        """
        Initializes a database with a unique id and username field
        """

        db = sqlite3.connect(self.path)
        cursor = db.cursor()

        cursor.execute('''CREATE TABLE if not exists {table} ({id} INTEGER PRIMARY KEY AUTOINCREMENT, {username} TEXT)'''
            .format(table = self.table, id = self.uniqueID, username = self.usernameField))

        db.commit()
        db.close()

    def _connect(self):
        """
        Connects to the database and sets some instance-specific information such as grabbing column headers
        """

        self.db = sqlite3.connect(self.path)
        self.cursor = self.db.cursor()

        self.columnInfo = [x for x in self.cursor.execute('''PRAGMA table_info({table})'''.format(table=self.table))]

    def columns(self):
        """
        returns stuff from the list in a kinda elegent manner.
        """
        return zip(*zip(*self.columnInfo)[1:3])


    #this is going to need magic
    def addUser(self, name):
        """
        adds a user to the database and initializes them with 0s for all items
        arguments:
            name - the name of the new user
        """

        self.cursor.execute('''INSERT INTO {table} ({fields}) VALUES ({insertions})'''
            .format(table = self.table, insertions = self._questionMarks(), fields = self._fields()), 
            self._insertions(name))
        self.db.commit()


    def _questionMarks(self):
        return ",".join("?" for x in xrange(self.tableLength+1))


    def _insertions(self, name):
        return (name,) + tuple(None for x in xrange(self.tableLength))


    def _fields(self):
        """
        returns all of the (non autoincrementing primary key) fields in the database as a comma separated list
        """
        return ",".join(list(zip(*self.columnInfo)[1])[1:])


    def addColumn(self, column, datatype="integer"):
        """
        adds a new type of item (course) to the database
        arguments:
            item - the name of the course
        """
        self.cursor.execute('''ALTER TABLE {table} ADD {column} {type}'''
            .format(table = self.table, type = datatype, column = column))
        self.db.commit()

    def delUser(self, name):
        """
        removes a user from the database
        arguments:
            name - the username of the user
        """
        pass

    def getUser(self, name):
        """
        returns the list of opinions for a given user
        arguments:
            name - the name of the user

        return: a tuple of values 0-5 corresponding to null or an opinion on a course/item
        """
        self.cursor.execute('''SELECT * FROM {table} where {username} = ? '''
            .format(table = self.table, username = self.usernameField), (name,))
        return self.cursor.fetchone()[1:]

    def getOpinion(self, user, item):
        """
        returns the user's opinion on a single item
        user - the name of the user
            item - the position of the item in the matrix of items, in other words, the first item is 0, things are
                indexed by their position in the matrix, not the database

        return: a value from 0-5 corresponding to null or an opinion on a course/item
        """
        pass

    def updateUser(self, user, values):
        """
        changes all of a user's opinions for items at once
        arguments:
            user - the name of the user
            values - an array of updated values
        """
        pass

    def updateSingleItem(self, user, item, value):
        """
        changes a user's opinion on a single item
        arguments:
            user - the name of the user
            item - the position of the item in the matrix of items, in other words, the first item is 0, things are
                indexed by their position in the matrix, not the database
            value - the new value of the item
        """
        pass
    


if __name__ == "__main__":
    database = Database()
    #database.addColumn("newOne2")
    database.addUser("them")
    print database.columns()
    print database.getUser("them")
    print database.getUser("me")


    print database.tableLength