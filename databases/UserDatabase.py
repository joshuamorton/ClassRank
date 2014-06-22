"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String
import time
import scrypt #info at https://bitbucket.org/mhallin/py-scrypt/src/55ba75e449556fa4f4c1ee7d255cb4c746f17b77/scrypt.py?at=default


class UserDatabase(object):
    """
    I have created a monster
    """

    def __init__(self, base_class, hashlength):
        class UserTable(base_class):
            __tablename__ = "users"
            user_id = Column(sqlalchemy.Integer, primary_key=True)
            user_name = Column(String(32), nullable=False)
            email_address = Column(String(64), nullable=False)
            password_hash = Column(String(hashlength), nullable=False)
            password_salt = Column(String(16), nullable=False)
            first_name = Column(String(16), nullable=True)
            last_name = Column(String(16), nullable=True)


        self.class_ = UserTable
    def create(self):
        return self.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = UserDatabase(sqlalchemy.ext.declarative.declarative_base(), 64).create()

