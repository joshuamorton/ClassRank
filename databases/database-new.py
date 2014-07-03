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
    def fetch_school_by_name(self, school):
        """
        returns a school object for a given name

        Searches the database for a school object with the given short name ("Georgia Tech")
        This search is "unsafe" and will therefore throw errors if the school does not exist

        Arguments:
            school -- the short name of the school to be found

        Errors:
            ItemDoesNotExistError -- rasied if there is no school found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A school object as defined in the SchoolDatabase class
        """

        with self.session_scope() as session:
            try:
                return session.query(self.school).filter(self.school.school_short == school_name).one()
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)
        

    def fetch_school_by_id(self, schoolid):
        """
        returns a school object by a given schoolid

        Searches the database for a school object with the given unique id (12345)
        This search is "unsafe" and will therefore throw errors if the school does not exist

        Arguments:
            schoolid -- the unique id of the school in the database

        Errors:
            ItemDoesNotExistError -- rasied if there is no school found
            MultipleResultsFound -- rasied if there are multiple items of the same id (which should be unique) in the database, indicative of major issues

        Return:
            A school object as defined in the SchoolDatabase class
        """

        with self.session_scope() as session:
            try:
                return session.query(self.school).get(schoolid)
            except sqlalchemy.orm.exc.ObjectDeletedError:
                raise ItemDoesNotExistError(DatabaseObjects.School, schoolid)


    def fetch_user_by_name(self, username):
        """
        returns a user object for a given username

        Searches the database for a user object with the given username ("jmorton")
        This search is "unsafe" and will therefore throw errors if the user does not exist

        Arguments:
            username -- the short name of the school to be found

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A user object as defined in the UserDatabase class
        """

        with self.session_scope() as session:
            try:
                return session.query(self.user).filter(self.user.user_name == username).one()
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.User, username)


    def fetch_user_by_id(self, userid):
        """
        returns a user object for a given username

        Searches the database for a user object with the given username ("jmorton")
        This search is "unsafe" and will therefore throw errors if the user does not exist

        Arguments:
            username -- the short name of the school to be found

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A user object as defined in the UserDatabase class
        """
        
        with self.session_scope() as session:
            try:
                return session.query(self.user).get(userid)
            except sqlalchemy.orm.exc.ObjectDeletedError:
                raise ItemDoesNotExistError(DatabaseObjects.User, username)


    def fetch_course_by_name(self, coursename, school, semester=None, year=None, professor=None):
        """
        returns a user object for a given username

        Searches the database for a course object for a given school and user
        This search is "unsafe" and will therefore throw errors if the course or school does not exist

        Arguments:
            coursename -- the short name of the course ("CS1301")
            school -- the schoolname for the school where the course is held ("Georgia Tech")
            semester -- (optional) the semester where the course is, a semester enum (Semesters.Summer)
            year -- (optional) the year of the course (2012)
            professor -- (optional) the professor who taught the course ("Greco")

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A course object as defined in the CourseDatabase class
        """

        with self.session_scope() as session:
            try:
                schoolid = session.query(self.school).filter(self.school.school_short == school_name).one().school_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)

            kwargs = {}
            kwargs["course_name"] = coursename
            kwargs["school_id"] = schoolid
            kwargs["semeser"] = semeser
            kwargs["year"] = year
            kwargs["professor"] = professor

            try:
                return session.query(self.course).filter(**kwargs).one()
            except:
                raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)



    def fetch_course_by_id(self, courseid):
        """
        returns a user object for a given username

        Searches the database for a course object for a given school and user
        This search is "unsafe" and will therefore throw errors if the course does not exist

        Arguments:
            courseid -- the unique id for the course (21345)

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A course object as defined in the CourseDatabase class
        """
        with self.session_scope() as session:
            try:
                session.query(self.course).get(courseid)
            except sqlalchemy.orm.exc.ObjectDeletedError:
                raise ItemDoesNotExistError(DatabaseObjects.Course, courseid)


    def fetch_rating_by_names(self, username, coursename, semester=None, year=None, professor=None):
        """
        returns a rating object for a given user/course combination

        Searches the database for a rating by a user for a specific course at their school
        This search is unsafe and will therefore throw errors if the course, user, school, or rating does not exist

        Arguments:
            username -- the username of the user who rated the course ("jmorton")
            coursename -- the short name of the course ("CS1301")
            semester -- (optional) the semester where the course is, a semester enum (Semesters.Summer)
            year -- (optional) the year of the course (2012)
            professor -- (optional) the professor who taught the course ("Greco")

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A rating object as defined in the RatingDatabase class
        """


        with self.session_scope() as session:
            try:
                user = session.query(self.user).filter(self.user.user_name == username).one()
                userid = user.user_id
                schoolid = school_school.id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.User, username)

            kwargs = {}
            kwargs["course_name"] = coursename
            kwargs["school_id"] = schoolid
            kwargs["semeser"] = semeser
            kwargs["year"] = year
            kwargs["professor"] = professor

            try:
                courseid = session.query(self.course).filter(**kwargs).one().course_id
            except:
                raise ItemDoesNotExistError(DatabaseObjects.Course, coursename)

            try:
                return session.query(self.rating).filter(self.rating.user_id == userid).filter(self.rating.course_id == courseid).one()
            except:
                raise ItemDoesNotExistError(DatabaseObjects.Rating, username+" for "+coursename)


    def fetch_rating_by_id(self, userid, courseid):
        """
        returns a rating object for a given userid/courseid combination

        Searches the database for a rating by a user for a specific course at their school
        This search is unsafe and will therefore throw errors if the course, user, school, or rating does not exist

        Arguments:
            userid -- the username of the user who rated the course (17)
            courseid -- the short name of the course (12345)

        Errors:
            ItemDoesNotExistError -- rasied if there is no item found
            MultipleResultsFound -- rasied if there are multiple items of the same name (which should be unique) in the database, indicative of major issues

        Return:
            A rating object as defined in the RatingDatabase class
        """
        with self.session_scope() as session:
            try:
                return session.query(self.rating).filter(self.rating.user_id == userid).filter(self.rating.course_id == courseid).one()
            except:
                raise ItemDoesNotExistError(DatabaseObjects.Rating, username+" for "+coursename)

    def school_exists(self, school):
        """

        """
        pass

    def user_exists(self, username):
        """
        """
        pass

    def course_exists(self, school, coursename, semester=None, year=None, professor=None):
        """
        """
        pass

    def add_school():
        """
        """
        pass

    #schools cannot be removed because that implies larger issues and can be done manually by admins

    def add_user():
        """
        """
        pass

    def remove_user():
        """
        """

    def add_course():
        """
        """
        pass

    def remove_course():
        """
        """
        pass

    def add_rating():
        """
        """
        pass

    def remove_rating():
        """
        """
        pass

    def update_rating(self, *args, **kwargs):
        """
        """
        self.add_rating(args, kwargs) #probable implementation

    def update_user():
        """
        """
        pass

    def update_course():
        """
        """
        pass

    def fetch_students():
        """
        """
        pass

    def fetch_courses():
        """
        """
        pass

    def check_password(self, username, password):
        """
        """
        return True

    def update_password(self, username, new_password):
        """
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


#A collection of error classes thrown when either things do or do not exist in the database
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


if __name__ == "__main__":
    #some unit testing, still leaves much to be desired, but ehh
    db = Database()
    # if not db.school_exists("Georgia Tech"):
    #     db.add_school("Georgia Institute of Technology", "Georgia Tech")
    # assert db.school_exists("Georgia Tech")
    # if not db.user_exists("jmorton"):
    #     db.add_user("jmorton", "Joshua.morton13@gmail.com", "password", "Georgia Tech", admin=True)
    # if not db.user_exists("njohnson"):
    #     db.add_user("njohnson", "Nick@johnson.com", "securepassword", "Georgia Tech", admin=True, first="Nick", last="Johnson")
    # if not db.course_exists("Georgia Tech", "CS1301"):
    #     db.add_course("Georgia Tech", "Introduction to Computer Science in Python", "CS1301")
    # print(db.courses)
    # db.rate("jmorton", "CS1301", 5)
    # if not db.school_exists("Harvard"):
    #     db.add_school("Harvard Univerity", "Harvard")
    # if not db.course_exists("Harvard", "CS50"):
    #     db.add_course("Harvard", "This is CS50", "CS50")
    # try:
    #     db.rate("jmorton", "CS50", 2)
    # except:
    #     x = "failed"
    # assert x == "failed"
    # print(db.fetch_rating("jmorton", "CS1301"))
    # if not db.course_exists("Georgia Tech", "CS1331"):
    #     db.add_course("Georgia Tech", "Introduction to OOP in Java", "CS1331")
    # if not db.course_exists("Georgia Tech", "CS1332"):
    #     db.add_course("Georgia Tech", "KickAss Datastructures class!", "CS1332")
    # db.rate("jmorton", "CS1331", 2)
    # db.rate("jmorton", "CS1332", 4)
    # print([db.fetch_rating("jmorton", item.identifier) for item in db.fetch_courses("jmorton")])