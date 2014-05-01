"""
The collaborative filtering portion of the system.
Should always eb used with databases
heavily modified version of the code here:
    https://github.com/uenowataru/CollaborativeFiltering/blob/master/CollaborativeFiltering.py
"""

import databases.Database as databases
import math

class CollaborativeFilter:
    """
    :function this: does something
    """

    def __init__(self, database, table, folder):
        """
        """
        self.dbViewer = databases.Viewer(database, table, folder)
        self.db = databases.Database(database, table, folder)
        self.weights = {}





if __name__ == "__main__":
    assert 1 == 1
    #do more
    x = CollaborativeFilter("database.db", "main", "databases/data")
    assert x.dbViewer.currentOpinions("them") == x.db.currentOpinions("them")
    print x.dbViewer.currentOpinions("them")
