"""
Database for storing ratings
"""

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, String


class RatingDatabase(object):
    """
    Factory for creating ratings databases
    """

    def __init__(this, base_class, course_):
        """
        Creates a class to store user data, based on some provided information
        """
        class RatingTable(base_class):
            """
            """
            __tablename__ = "ratings"
            # creation info
            user_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.user_id"), primary_key=True)
            course_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("courses.course_id"), primary_key=True)
            # attributes
            rating = Column(sqlalchemy.Integer, nullable=True)  # how much one liked the course wholistically
            grade = Column(sqlalchemy.Integer, nullable=True)  # how well the student did
            rigor = Column(sqlalchemy.Integer, nullable=True)  # overall how challenging the course was
            utility = Column(sqlalchemy.Integer, nullable=True)
            # these two are the difference between, for example, a course with assignments that are 300 simple math problems
            # and a course where assignments are 1-2 immensly difficult proofs, such things appeal to different people
            workload = Column(sqlalchemy.Integer, nullable=True)  # how much work was given
            difficulty = Column(sqlalchemy.Integer, nullable=True)  # how hard assignments were
            time = Column(sqlalchemy.Integer, nullable=True)  # hours spent out of class per week

            #professor related stuff
            attendence = Column(sqlalchemy.Integer, nullable=True)  # some metric for how relevant attendence is
            professor = Column(sqlalchemy.Integer, nullable=True)  # how good the professor is
            interactivity = Column(sqlalchemy.Integer, nullable=True)  # a metric for how much the prof interacts with students

            year = Column(sqlalchemy.Integer, nullable=True)  # year you took it
            professor = Column(String(64), nullable=True)  # prof that taught it
            semester = Column(String(4), nullable=True)  # semester, spr, sum, fall, wint
            # relations
            course = sqlalchemy.orm.relationship(course_, backref="ratings")

            def __str__(self):
                """
                """
                return self.__repr__()

            def __repr__(self):
                """
                """
                return "<Rating of {} by user {} for course {}>".format(self.rating, self.course_id, self.user_id)

        this.class_ = RatingTable

    def create(this):
        """
        Returns the UserTable class
        """
        return this.class_


if __name__ == "__main__":
    meta = sqlalchemy.MetaData()
    testdb = RatingDatabase(sqlalchemy.ext.declarative.declarative_base(), "test").create()
