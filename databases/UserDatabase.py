"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class UserDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class, hashlength):
        """
        This instantiates an object with the given settings (namely hashlength)
            and returns an instance of the new class when create is called

        This also allows additional class specific methods to be added to the
            class, for example if hashing were to be handled within the user
            class instead of in the database overall class it could be done that
            way.
        """
        class UserTable(base_class):
            __tablename__ = "users"
            user_id = Column(sqlalchemy.Integer, primary_key=True)
            user_name = Column(String(32), nullable=False)
            email_address = Column(String(64), nullable=False)
            password_hash = Column(String(hashlength), nullable=False)
            password_salt = Column(String(16), nullable=False)
            first_name = Column(String(16), nullable=True)
            last_name = Column(String(16), nullable=True)

            def __str__(self):
                return self.__repr__()

            def __repr__(self):
                return "<User {} ({} {}) at {}>".format(self.user_name, self.first_name or "", self.last_name or "", self.email_address) 


        this.class_ = UserTable
    def create(this):
        """
        returns an instance of the new class, should basically always be run
        unless something strange is happening
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = UserDatabase(sqlalchemy.ext.declarative.declarative_base(), 64).create()

