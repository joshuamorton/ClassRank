"""
The collaborative filtering portion of the system.
Should always eb used with databases
heavily modified version of the code here:
    https://github.com/uenowataru/CollaborativeFiltering/blob/master/CollaborativeFiltering.py
"""

import databases
import math

class CollaborativeFilter:
    """
    :function this: does something
    """

    def __init__(self, database, table):
        """
        :param that: represents something
        """
        self.dbViewer = databases.Viewer(database, table)






if __name__ == "__main__":
    assert 1 == 1
    #do more