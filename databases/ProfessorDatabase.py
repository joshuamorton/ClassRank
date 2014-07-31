"""
Database for storing users
"""

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
from sqlalchemy import Column, String


class ProfessorDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class, course_, school_):
        """
        This instantiates an object with the given settings
            and returns an instance of the new class when create is called

        This also allows additional class specific methods to be added to the
            class, for example if hashing were to be handled within the user
            class instead of in the database overall class it could be done that
            way.

        groups are the group that a user belongs to, currently only one is possible.
        """

        class ProfessorTable(base_class):
            """
            """
            __tablename__ = "professors"
            # signup info
            prof_id = Column(sqlalchemy.Integer, primary_key=True)
            # personal information
            name = Column(String(32), nullable=False)

            linked_user_account = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), nullable=True)
            school_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("schools.school_id"))
            sections = sqlalchemy.orm.relationship(course_, backref="professor")
            school = sqlalchemy.orm.relationship(school_, backref="professors")

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Professor {} at {}>".format(self.name, self.school_id)

        this.class_ = ProfessorTable

    def create(this):
        """
        returns an instance of the new class, should basically always be run
        unless something strange is happening
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
