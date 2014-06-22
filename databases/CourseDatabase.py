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

    def __init__(self, base_class):
        class UserTable(base_class):
            __tablename__ = "courses"
            course_id = Column(sqlalchemy.Integer, primary_key=True)
            course_name = Column(String(64), nullable=True)
            identifier = Column(String(16), nullable=False)

        self.class_ = UserTable
    def create(self):
        return self.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = CourseDatabase(sqlalchemy.ext.declarative.declarative_base()).create()

