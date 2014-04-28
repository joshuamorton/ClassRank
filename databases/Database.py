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
        return zip(*zip(*self.columnInfo)[1:3])




if __name__ == "__main__":
    database = Database()
    print database.columns()