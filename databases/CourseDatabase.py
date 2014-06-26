"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String
import time


class CourseDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class):
        class UserTable(base_class):
            __tablename__ = "courses"
            course_id = Column(sqlalchemy.Integer, primary_key=True)
            course_name = Column(String(64), nullable=True)
            identifier = Column(String(16), nullable=False)
            

            def __str__(self):
                return self.__repr__()

            def __repr__(self):
                return "<Course {} ({})>".format(self.identifier, self.course_name) 

        this.class_ = UserTable
    def create(this):
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = CourseDatabase(sqlalchemy.ext.declarative.declarative_base()).create()
