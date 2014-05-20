"""
The collaborative filtering portion of the system.
Should always be used with databases.database
"""

import math

import databases.database as databases
import math

class CollaborativeFilter:
    """
    A Collaborative Filtering algorithm/object meant to be heavily optimized for speed
    """

    def __init__(self, *args):
        """
        """

        self.