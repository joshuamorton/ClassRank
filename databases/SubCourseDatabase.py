"""
Database for storing course information
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, Enum


class SubCourseDatabase(object):
    """
    I have created a monster
    """

    def __init__(this, base_class, course_):
        """
        """

        class SubCourseTable(base_class):
            """
            """
            __tablename__ = "sections"
            # creation info
            section_id = Column(sqlalchemy.Integer, primary_key=True)
            parent_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("courses.school_id"))
            # optional info
            professor_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("professors.prof_id"))
            year = Column(sqlalchemy.Integer, nullable=True)
            semester = Column(Enum("Spring", "Summer", "Fall", "Winter"), nullable=True)

            sqlalchemy.UniqueConstraint("parent_id", "professor", "year", "semester")
            course = sqlalchemy.orm.relationship(course_, backref="sections")



            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Course {} ({})>".format(self.identifier, self.course_name)

        this.class_ = SubCourseTable

    def create(this):
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
