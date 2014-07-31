"""
drop in (hopefully) replacement for the database class
developed by Joshua Morton

Now with (even) more DRY!

"""

from enum import Enum
from contextlib import contextmanager
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import time  # for creating hash salts
import scrypt  # for hashing passwords
import hashlib  # for api keys

from . import UserDatabase
from . import CourseDatabase
from . import RatingDatabase
from . import SchoolDatabase
from . import ProfessorDatabase
from . import SubCourseDatabase
from . import SubjectDatabase

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

    def __init__(self, name="ClassRank.db", folder="data", hashlength=64):
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
        self.subject = SubjectDatabase.SubjectDatabase(self.base).create()
        self.course = CourseDatabase.CourseDatabase(self.base).create()
        self.rating = RatingDatabase.RatingDatabase(self.base, self.course).create()
        self.user = UserDatabase.UserDatabase(self.base, self.hashlength, self.course, self.rating).create()
        self.school = SchoolDatabase.SchoolDatabase(self.base, self.course, self.user).create()
        self.section = SubCourseDatabase.SubCourseDatabase(self.base, self.course).create()
        self.professor = ProfessorDatabase.ProfessorDatabase(self.base, self.section).create()

        self.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = None

        # on first run, create an admin account
        if len(self.schools) == 0:
            with self as db:
                db += db.new_school("Admin Academy", "Admin")
                db += db.new_user("Admin", "admin@admin.admin", "password", "Admin", admin=True, moderator=True)

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


    def new_school(self, name, abbreviataion):
        """
        """
        return self.school(school_name=name, school_short=abbreviataion)


    def new_user(self, username, email, password, school, admin=False, moderator=False, professor=False):
        """
        must be used inside the construct "with self as database:"
        """
        try:
            school_id = self.session.query(self.school).filter_by(school_short=school).one().school_id
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)

        pwsalt = str(int(time.time()))
        pwhash = scrypt.hash(password, pwsalt, self.hashlength)
        apikey = hashlib.sha256(pwhash).hexdigest()
        
        return self.user(school_id = school_id, user_name=username, email_address=email, password_hash=pwhash, password_salt=pwsalt, apikey=apikey, admin=admin, moderator=moderator, professor=professor)


    def new_course(self, school, name, identifier, subject=None):
        """
        must be used inside the construct "with self as database:"
        """
        try:
            school_id = self.session.query(self.school).filter_by(school_short=school).one().school_id
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)

        if subject is not None:
            try:
                subject_id = self.session.query(self.subject).filter_by(name=subject).one().subject_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.Subject, name)
        else:
            subject_id = None

        return self.course(school_id=school_id, course_name=name, identifier=identifier, subject=subject_id)


    def new_section(self,):
        pass

    def new_subject(self,):
        pass

    def new_professor(self,):
        pass

    def new_rating(self,):
        pass


    def __iadd__(self, other):
        """
        """
        if self.session is not None:
            self.session.add(other)
        else:
            with self.session_scope() as session:
                session.add(other)
        return self


    def __enter__(self):
        """
        syntactic sugar for adding and removing courses and such
        """
        self.session = self.sessionmaker()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        """
        the sugariest of syntaxes
        """
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
            self.session = None

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
    def ratings(self):
        with self.session_scope() as session:
            return session.query(self.rating).all()
    
    @property
    def courses(self):
        """
        property, all courses in the db
        """
        with self.session_scope() as session:
            return session.query(self.course).all()

    @property
    def subjects(self):
        with self.session_scope() as session:
            return session.query(self.subject).all()


#A collection of error classes raised when either things do or do not exist in the database
class DatabaseObjects(Enum):
    """
    So enums are beautiful and I love them
    """
    School = "School"
    User = "User"
    Course = "Course"
    Rating = "Rating"
    Section = "Section"
    Professor = "Professor"
    Subject = "Subject"


class Semesters(Enum):
    """
    """
    Spring = "Spring"
    Summer = "Summer"
    Fall = "Fall"
    Winter = "Winter"


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

class NoSessionError(Exception):

    def __str__(self):
        return "There was no accessible database session availible"


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

