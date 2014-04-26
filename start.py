"""
Initializes databases

"""

import sqlite3

def createDatabases():

    #the sparse live database is the database that is updated live as people tell the system what they do and don't like
    db = sqlite3.connect("data/Live.db")
    cursor = db.cursor()
    try:
        cursor.execute('''CREATE TABLE opinions(username text, array text)''')
    except:
        pass
    db.commit()
    db.close()

    #Cached is the database that the webserver queries with questions about who likes what.  A worker ocassionally copies "Live" to
    #work in the background to update Cached to what it needs to be
    db = sqlite3.connect("data/Cached.db")
    cursor = db.cursor()
    try:
        cursor.execute('''CREATE TABLE opinions(username text, array text)''')
    except:
        pass
    db.commit()
    db.close()

if __name__ == "__main__":
    createDatabases()

