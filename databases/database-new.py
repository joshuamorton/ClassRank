"""
drop in (hopefully) replacement for the database class
developed by Joshua Morton

Now with more DRY!

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
        initializes the database, creates tables and files as necessary

        Keyword Arguments:
            name -- the name of the database file, created as necessary
            table -- the table, a holdover from previous versions, can be ignored
            folder -- a relative path to the folder where the database should be stored 
            uid -- the value under which the database stores the user's Primary Key, holdover can be safely ignored
            hashlength -- the length of password hashes

        The system defaults to name="ClassRank.db", table="main" folder="data", uid="user_id, and hashlength="64"
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
            `with Database.session_scope() as session: #or similar`
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


    #methods that do things!
    def fetch_school_by_name(self, session, school_name): #done
        """
        """
        try:
            return session.query(self.school).filter(self.school.school_short == school_name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)


    def fetch_school_by_id(self, session, schoolid): #done
        """
        """
        try:
            return session.query(self.school).get(schoolid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.School, schoolid)


    def fetch_user_by_name(self, session, user): #done
        """
        """
        try:
            return session.query(self.user).filter(self.user.user_name == username).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.User, username)


    def fetch_user_by_id(self, session, userid): #done
        """
        """
        try:
            return session.query(self.user).get(userid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.User, username)


    def fetch_course_by_name(self, session, school, coursename, semester=None, year=None, professor=None): #done, might want to clean it
        """
        """
        try:
            schoolid = session.query(self.school).filter(self.school.school_short == school).one().school_id
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)

        query = {}
        query["course_name"] = coursename
        query["school_id"] = schoolid

        if semester:
            query["semester"] = semester
        if year:
            query["year"] = year
        if professor:
            query["professor"] = professor

        try:
            return session.query(self.course).filter_by(**query).one()
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)


    def fetch_course_by_id(self, session, courseid): #done
        """
        """
        try:
            return session.query(self.course).get(courseid)
        except sqlalchemy.orm.exc.ObjectDeletedError:
            raise ItemDoesNotExistError(DatabaseObjects.Course, courseid)


    def fetch_rating_by_name(self, session, username, coursename, semester=None, year=None, professor=None): #done
        """
        """
        try:
            user = session.query(self.user).filter(self.user.user_name == username).one()
            userid = user.user_id
            schoolid = user.school_id
        except:
            raise ItemDoesNotExistError(DatabaseObjects.User, username)



        query = {}
        query["course_name"] = coursename
        query["school_id"] = schoolid

        if semester:
            query["semester"] = semester
        if year:
            query["year"] = year
        if professor:
            query["professor"] = professor

        try:
            courseid = session.query(self.course).filter_by(**query).one().course_id
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)

        try:
            return session.query(self.rating).filter_by(user_id == userid, course_id == courseid).one()
        except:
            raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)


    def fetch_rating_by_id(self, session, userid, courseid): #done
        try:
            return session.query(self.rating).filter(self.rating.user_id == userid).filter(self.rating.course_id == courseid).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.Rating, username+" for "+coursename)


    def school_exists(self, session, school_name=None, school_id=None, school_short=None):
        try:
            session.query(self.school).filter()
        except:
            pass

    def user_exists(self, session, user_name=None, user_id=None, email_address=None):
        pass

    def course_exists(self, session, coursename, semester=None, year=None, professor=None):
        pass

    def rating_exists(self, session, username, coursename, semester=None, year=None, professor=None):
        pass

    def add_school(self, session, school_name, school_identifier):
        #update this
        session.add(self.school(school_name=school_name, school_short=school_identifier))


    def add_user(self, session, username, email, password, school, first=None, last=None, admin=False, mod=False):
        pass

    def add_course(self, session, school, coursename, identifier, professor=None, year=None, semester=None):
        #also update, remove schoolid=None
        schoolid = self.fetch_school_by_name(session, school).school_id
        session.add(self.course(course_name=coursename, school_id=schoolid, identifier=identifier, professor=professor, year=year, semester=semester))


    def add_rating(self, session, username, coursename, semester=None, year=None, professor=None, rating=None, grade=None, difficulty=None):
        pass

    def remove_rating(self, session, username, coursename):
        pass

    def remove_user(self, session, username):
        pass

    #neither schools nor courses can be removed

    def update_user(self, session, username, email=None, password=None, first=None, last=None, age=None, grad=None, admin=None, mod=None):
        pass

    def update_course(self, session, school, coursename, identifier=None, semester=None, year=None, professor=None):
        pass

    def update_rating(self, session, username, coursename, semester=None, year=None, professor=None, rating=None, grade=None, difficulty=None):
        pass

    def fetch_students(self, session, school):
        """
        """
        pass


    def fetch_courses(self, session, user):
        """
        """
        pass


    def check_password(self, session, username, password):
        """
        """
        return True


    def update_password(self, session, username, new_password):
        """
        """
        pass




    def __enter__(self):
        """
        syntactic sugar
        """
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        """
        the sugariest of syntaxes
        """
        pass



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


#A collection of error classes raised when either things do or do not exist in the database
class DatabaseObjects(Enum):
    """
    So enums are beautiful and I love them
    """
    School = "School"
    User = "User"
    Course = "Course"
    Rating = "Rating"


class Semesters(Enum):
    """
    """
    Spring = "Spr"
    Summer = "Sum"
    Fall = "Fall"
    Winter = "Win"


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

class PasswordLengthError(Exception):
    """
    Exception raised when a user's password is too long (hashing 2000 char passwords is bad)
    """
    def __init__(self, user, password):
        self.password = password
        self.user = user

    def str(self):
        return "User {}'s password ({}) is too long".format(self.user, self.password)


if __name__ == "__main__":
    #some unit testing, still leaves much to be desired, but ehh
    db = Database()
    with db.session_scope() as session:
        db.add_school(session, "derp", "derpina")
        db.add_course(session, "derpina","CS131", "CSBABY!")
        session.commit()
        assert db.fetch_course_by_name(session, "derpina", "CS131")

