"""
File for testing database-y and threading-y stuff

"""

import sqlite3

db = sqlite3.connect("data/persistent.db")

cursor = db.cursor()
try:
    cursor.execute('''CREATE TABLE opinions(username text, array text)''')
except:
    pass

cursor.execute("INSERT INTO opinions VALUES ('admin','%s')" % str([0,1,2,3,4,5,6,7,8]))
for row in cursor.execute('SELECT * FROM opinions ORDER BY username'):
        print row
db.commit()
db.close()