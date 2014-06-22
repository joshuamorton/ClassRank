"""
drop in (hopefully) replacement for the database class

scrypt hash format
def hash(password, salt, N=1 << 14, r=8, p=1, buflen=64):
"""

from contextlib import contextmanager
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import UserDatabase
import CourseDatabase
import RatingDatabase
import time  # for creating hash salts
import scrypt  # for hashing passwords


class Database(object):
    """
    The main database that all other parts of the app interface with.
    """

    def __init__(self, name="ClassRank.db", table="main", folder="data", uid="user_id"):
        """
        """
        self.engine = sqlalchemy.create_engine('sqlite:///'+folder+'/'+name)

        self.hashlength = 64  # length of the scrypt password hash
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.metadata = self.base.metadata

        # the three main parts of the overall database system
        self.user = UserDatabase.UserDatabase(self.base, self.hashlength).create()
        self.course = CourseDatabase.CourseDatabase(self.base).create()
        self.rating = RatingDatabase.RatingDatabase(self.base).create()

        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    # the rest is just abstraction to make life less terrible

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        use the syntax
            with self.session_scope() as session: #or similar
        for operations requiring a session
        """
        session = self.sessionmaker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_user(self, username, email, password, first=None, last=None):
        """
        """
        with self.session_scope() as session:
            if session.query(self.user).filter(self.user.user_name == username).all():
                raise UserExistsError(username)
            now = str(int(time.time()))
            pw_hash = scrypt.hash(password, now, buflen=self.hashlength)
            session.add(self.user(user_name=username, email_address=email, password_hash=pw_hash, password_salt=now, first_name=first, last_name=last))

    def user_exists(self, username):
        """
        """
        with self.session_scope() as session:
            if session.query(self.user).filter(self.user.user_name == username).all():
                return True
            return False

    def add_course(self, name, course_identifier):
        """
        """
        with self.session_scope() as session:
            if session.query(self.course).filter(self.course.identifier == course_identifier).all():
                raise CourseExistsError(course_identifier)
            session.add(self.course(course_name=name, identifier=course_identifier))

    def rate(self, user, course, rating):
        """
        A general interface for rating, doesn't care whether or not there is
            already a rating for a given course.  If the rating exists, it
            updates the existing rating.  Otherwise it creates it.
        """
        with self.session_scope() as session:
            try:
                uid = session.query(self.user).filter(self.user.user_name == user).all()[0].user_id
            except:
                raise UserExistsError(user)

            try:
                courseid = session.query(self.course).filter(self.course.identifier == course).all()[0].course_id
            except:
                raise CourseExistsError(course)

            if session.query(self.rating).filter(self.rating.user_id == uid).filter(self.rating.course_id == courseid).all():
                session.query(self.rating).filter(self.rating.user_id == uid).filter(self.rating.course_id == courseid).update({"rating": rating})
            else:
                session.add(self.rating(user_id=uid, course_id=courseid, rating=rating))

    def remove_rating(self, user, item):
        """
        This is equivalent to setting the rating to None
        """
        self.rate(user, item, None)

    def fetch_rating(self, user, course):
        """
        """
        with self.session_scope() as session:
            userid = session.query(self.user).filter(self.user.user_name == user).one().user_id
            courseid = session.query(self.course).filter(self.course.identifier == course).one().course_id
            return session.query(self.rating).filter(self.rating.user_id == userid).filter(self.rating.course_id == courseid).one().rating or None



# errors thrown by the above
class UserExistsError(Exception):
    """
    Exception raised when a user is already in the database
    """
    def __init__(self, username):
        super.__init__()
        self.username = username

    def __str__(self):
        return "A user named {} already exists".format(self.username)


class CourseExistsError(Exception):
    """
    Exception raised when a user is already in the database
    """
    def __init__(self, identifier):
        super.__init__()
        self.identifier = identifier

    def __str__(self):
        return "The course {} already exists".format(self.identifier)


if __name__ == "__main__":
    db = Database()
    print(db.user_exists("me"))
    db.add_user("me", "me@my.domain", "password", first="Joshua", last="Morton")
    db.add_user("you", "you@yourwebsite", "insecure")
    db.add_course("Introduction to Computer Science in Matlab", "CS1371")
    db.add_course("Calculus 2", "MATH1502")
    db.rate("me", "MATH1502", 4)
    db.rate("you", "MATH1502", 2)
    session = db.sessionmaker()
    assert session.query(db.rating).filter(db.rating.user_id == session.query(db.user).filter(db.user.user_name == "me").one().user_id).filter(db.rating.course_id == session.query(db.course).filter(db.course.identifier == "MATH1502").one().course_id).one().rating == 4
    print(session.query(db.user).filter(db.user.user_name == "me").one())
    session.close()
    db.remove_rating("me", "MATH1502")
    db.rate("me", "MATH1502", 25)
    print(db.fetch_rating("me", "MATH1502"))
