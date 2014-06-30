"""
drop in (hopefully) replacement for the database class

scrypt hash format
def hash(password, salt, N=1 << 14, r=8, p=1, buflen=64):
"""

from enum import Enum
from contextlib import contextmanager
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import UserDatabase
import CourseDatabase
import RatingDatabase
import SchoolDatabase
import time  # for creating hash salts
import scrypt  # for hashing passwords


class Database(object):
    """
    An abstraction of an sql database for managing user and class information.

    instance data that might be relevant:
        hashlength -- the length of password hashes
        course -- the table of courses
        rating -- the table of ratings (many to many link between course and user)
        user -- the table of users
        school -- the table of school (one to many with user and course)
        sessionmaker -- a factory for sessions, can be used by external tools to make specialized database queries
    """

    def __init__(self, name="ClassRank.db", table="main", folder="data", uid="user_id", hashlength=64):
        """
        Initializes the database, creates it as necessary

        Keyword Arguments:
            name -- the name of the database file, created as necessary
                default: "ClassRank.db"
            table -- the table, a holdover from previous versions, can be ignored
                default: "main"
            folder -- a relative path to the folder where the database should be stored 
                default: "data"
            uid -- the value under which the database stores the user's Primary Key, holdover can be safely ignored
                default: user_id
            hashlength -- the length of password hashes
                default: 64
        """
        self.engine = sqlalchemy.create_engine('sqlite:///'+folder+'/'+name)

        self.hashlength = hashlength  # length of the scrypt password hash
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.metadata = self.base.metadata

        # the three main parts of the overall database system
        self.course = CourseDatabase.CourseDatabase(self.base).create()
        self.rating = RatingDatabase.RatingDatabase(self.base, self.course).create()
        self.user = UserDatabase.UserDatabase(self.base, self.hashlength, self.course, self.rating).create()
        self.school = SchoolDatabase.SchoolDatabase(self.base, self.course, self.user).create()

        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)


    # the rest is just abstraction to make life less terrible
    @contextmanager
    def session_scope(self):
        """
        database session factory wrapper

        Provide a transactional scope around a series of operations.  use the syntax
            `with self.session_scope() as session: #or similar`
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


    def add_user(self, username, email, password, school, first=None, last=None, admin=False, mod=False):
        """
        adds a new user to the database
        """
        with self.session_scope() as session:
            try:
                schoolid = session.query(self.school).filter(self.school.school_short == school).one().school_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)

            if session.query(self.user).filter(self.user.user_name == username).all():
                raise ItemExistsError(DatabaseObjects.User, username)
            now = str(int(time.time()))
            pw_hash = scrypt.hash(password, now, buflen=self.hashlength)
            session.add(self.user(user_name=username, email_address=email, password_hash=pw_hash, password_salt=now, school_id=schoolid, first_name=first, last_name=last, admin=admin, moderator=mod))

    def remove_user(self, username):
        """
        entirely removes an existing user from the database

        removes all ratings for the user as well as removing the user's user entry

        Arguments:
            username -- the username of the user to be remove
        """
        with self.session_scope() as session:
            user_id = session.query(self.user).filter(self.user.user_name == username).user_id
            session.delete(self.course).where(self.course.user_id == user_id)
            session.delete(self.user).where(self.user.user_id == user_id)


    def school_exists(self, school_name):
        """
        checks to see if a school of the given name is in the database

        Arguments:
            school_name -- the short name of the school
        """
        with self.session_scope() as session:
            if session.query(self.school).filter(self.school.school_short == school_name).all():
                return True
            return False


    def add_school(self, school_name, school_short):
        """
        adds a new school to the database
        """
        with self.session_scope() as session:
            if session.query(self.school).filter(self.school.school_short == school_short).all():
                raise ItemExistsError(DatabaseObjects.School, school_short)
            session.add(self.school(school_name=school_name, school_short=school_short))


    def course_exists(self, school_name, course_identifier):
        """
        checks to see if a course of a given name is in the database
        """
        with self.session_scope() as session:
            try:
                school = session.query(self.school).filter(self.school.school_short == school_name).one()
            except:
                raise ItemDoesNotExistError(DatabaseObjects.School, school_name)

            if session.query(self.course).filter(self.course.school == school).filter(self.course.identifier == course_identifier).all():
                return True
            return False


    def user_exists(self, username):
        """
        checks to see if a user of a given username is in the database
        """
        with self.session_scope() as session:
            if session.query(self.user).filter(self.user.user_name == username).all():
                return True
            return False


    def add_course(self, school, name, course_identifier):
        """
        adds a new course to the database
        """
        with self.session_scope() as session:
            try:
                schoolid = session.query(self.school).filter(self.school.school_short == school).one().school_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)

            if session.query(self.course).filter(self.course.identifier == course_identifier).filter(self.course.school_id == schoolid).all():
                raise ItemExistsError(DatabaseObjects.Course, course_identifier)
            session.add(self.course(course_name=name, identifier=course_identifier, school_id=schoolid))


    def rate(self, user, course, rating):
        """
        provides a general interface to

        A general interface for rating, doesn't care whether or not there is
            already a rating for a given course.  If the rating exists, it
            updates the existing rating.  Otherwise it creates it.
        """
        with self.session_scope() as session:
            try:
                user = session.query(self.user).filter(self.user.user_name == user).one()
                uid = user.user_id
                schoolid = user.school_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.User, user)

            try:
                courseid = session.query(self.course).filter(self.course.school_id == schoolid).filter(self.course.identifier == course).all()[0].course_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.Course, course)


            if session.query(self.rating).filter(self.rating.user_id == uid).filter(self.rating.course_id == courseid).all():
                session.query(self.rating).filter(self.rating.user_id == uid).filter(self.rating.course_id == courseid).update({"rating": rating})
            else:
                session.add(self.rating(user_id=uid, course_id=courseid, rating=rating))


    def remove_rating(self, user, item):
        """
        removes a rating for a user by setting it to None

        """
        self.rate(user, item, None)


    def fetch_rating(self, user, course):
        """
        returns the rating for a user 
        """
        with self.session_scope() as session:
            try:
                user = session.query(self.user).filter(self.user.user_name == user).one()
                uid = user.user_id
                schoolid = user.school_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.User, user)
            courseid = session.query(self.course).filter(self.course.school_id == schoolid).filter(self.course.identifier == course).one().course_id
            return session.query(self.rating).filter(self.rating.user_id == uid).filter(self.rating.course_id == courseid).one().rating or None

    def fetch_school(self, school_name):
        """
        """
        with self.session_scope() as session:
            return session.query(self.school).filter(self.school.school_short == school_name).one()

    def fetch_course(self, school, course):
        """
        """
        with self.session_scope() as session:
            try:
                schoolid = session.query(self.school).filter(self.school.school_short == school).one().school_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)
            return session.query(self.course).filter(self.course.school_id == schoolid).filter(self.course.identifier == course).one()

    def fetch_user(self, username):
        """
        """
        with self.session_scope() as session:
            return session.query(self.user).filter(self.user.user_name == username).one()

    @property
    def users(self):
        """
        property, all users in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).all()
    

    @property
    def moderators(self):
        """
        property, all moderators in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).filter(self.user.moderator == True).all()


    @property
    def admins(self):
        """
        property, all administrators in the database
        """
        with self.session_scope() as session:
            return session.query(self.user).filter(self.user.admin == True).all()


    @property
    def schools(self):
        """
        property, all schools in the database
        """
        with self.session_scope() as session:
            return session.query(self.school).all()

    @property
    def courses(self):
        """
        property, all courses in the db
        """
        with self.session_scope() as session:
            return session.query(self.course).all()


#A collection of error classes thrown when either things do or do not exist in the database
class DatabaseObjects(Enum):
    """
    So enums are beautiful and I love them
    """
    School = "School"
    User = "User"
    Course = "Course"
    Rating = "Rating"


class ItemExistsError(Exception):
    """
    Exception raised when an item is already in the database
    """
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def __str__(self):
        return "A {} named {} already exists".format(self.identifier.name, self.name)


class ItemDoesNotExistError(Exception):
    """
    Exception raised when an item is not in the database
    """
    def __init__(self, identifier, name, *args):
        self.identifier = identifier
        self.name = name
        self.information = args

    def __str__(self):
        return "A {} named {} does not exist".format(self.identifier.name, self.name)


if __name__ == "__main__":
    #some unit testing, still leaves much to be desired, but ehh
    db = Database()
    if not db.school_exists("Georgia Tech"):
        db.add_school("Georgia Institute of Technology", "Georgia Tech")
    assert db.school_exists("Georgia Tech")
    if not db.user_exists("jmorton"):
        db.add_user("jmorton", "Joshua.morton13@gmail.com", "password", "Georgia Tech", admin=True)
    if not db.user_exists("njohnson"):
        db.add_user("njohnson", "Nick@johnson.com", "securepassword", "Georgia Tech", admin=True, first="Nick", last="Johnson")
    if not db.course_exists("Georgia Tech", "CS1301"):
        db.add_course("Georgia Tech", "Introduction to Computer Science in Python", "CS1301")
    print(db.courses)
    db.rate("jmorton", "CS1301", 5)
    if not db.school_exists("Harvard"):
        db.add_school("Harvard Univerity", "Harvard")
    if not db.course_exists("Harvard", "CS50"):
        db.add_course("Harvard", "This is CS50", "CS50")
    db.rate("jmorton", "CS50", 2)
    print(db.fetch_rating("jmorton", "CS1301"))
