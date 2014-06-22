"""
drop in (hopefully) replacement for the database class
scrypt hash format
def hash(password, salt, N=1 << 14, r=8, p=1, buflen=64):

"""

from sqlalchemy import Column, String
import sqlalchemy
import os.path
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import UserDatabase
import CourseDatabase
import RatingDatabase
import time
import scrypt

class Database(object):
    """
    The main database that all other parts of the system will interface with
    """

    def __init__(self, name="database.db", table="main", folder="data", uid="user_id"):
        """
        """
        self.engine = engine = sqlalchemy.create_engine('sqlite:///data/ClassRank.db')

        self.hashlength = 64 #length of the scrypt password hash
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.metadata = self.base.metadata


        self.user = UserDatabase.UserDatabase(self.base, self.hashlength).create()
        self.course = CourseDatabase.CourseDatabase(self.base).create()
        self.rating = RatingDatabase.RatingDatabase(self.base).create()
        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.sessionmaker()

if __name__ == "__main__":
    db = Database()
    math1502 = db.course()
    math1502.course_name = "Calculus 2"
    math1502.identifier = "MATH1502"
    now = str(int(time.time()))
    josh = db.user(user_name="joshuamorton", email_address="joshua.morton13@gmail.com", password_hash=scrypt.hash("password", now, buflen=hashlength), password_salt=now)
    db.session.add(math1502)
    db.session.add(josh)
    print(db.session.query(db.user).filter(db.user.user_name == "joshuamorton").one())
    josh1502 = db.rating(user_id=db.session.query(db.user).filter(db.user.user_name == "joshuamorton").one().user_id, course_id=db.session.query(db.course).filter(db.course.identifier == "MATH1502").one().course_id, rating=5)
    # for user in db.session.query(db.user).filter(db.user.user_name == "joshuamorton"):
        # print(user.password_hash)
    db.session.add(josh1502)
    db.session.commit()
    print(db.session.query(db.rating).first().course_id)
