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

    def __init__(this, base_class):
        class UserTable(base_class):
            __tablename__ = "ratings"
            user_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id") ,primary_key=True)
            course_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("courses.course_id") ,primary_key=True)
            rating = Column(sqlalchemy.Integer, nullable=True)

            def __str__(self):
                return self.__repr__()

            def __repr__(self):
                return "<Rating of {} by user {} for course {}>".format(self.rating, self.course_id, self.user_id) 

        this.class_ = UserTable
    def create(this):
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = RatingDatabase(sqlalchemy.ext.declarative.declarative_base()).create()

