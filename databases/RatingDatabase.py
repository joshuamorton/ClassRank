"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String
import time


class RatingDatabase(object):
    """
    I have created a monster
    """

    def __init__(self, base_class):
        class UserTable(base_class):
            __tablename__ = "ratings"
            user_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id") ,primary_key=True)
            course_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("courses.course_id") ,primary_key=True)
            rating = Column(sqlalchemy.Integer, nullable=True)


        self.class_ = UserTable
    def create(self):
        return self.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = RatingDatabase(sqlalchemy.ext.declarative.declarative_base()).create()

