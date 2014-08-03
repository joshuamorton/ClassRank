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

import UserDatabase
import CourseDatabase
import RatingDatabase
import SchoolDatabase
import ProfessorDatabase
import SubCourseDatabase
import SubjectDatabase

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

        # the tables in the database, some rely on previous ones to be correctly instantiated
        self.subject = SubjectDatabase.SubjectDatabase(self.base).create()
        self.course = CourseDatabase.CourseDatabase(self.base).create()
        self.section = SubCourseDatabase.SubCourseDatabase(self.base, self.course).create()
        self.rating = RatingDatabase.RatingDatabase(self.base, self.section).create()
        self.user = UserDatabase.UserDatabase(self.base, self.hashlength, self.section, self.rating).create()
        self.school = SchoolDatabase.SchoolDatabase(self.base, self.course, self.user).create()
        self.professor = ProfessorDatabase.ProfessorDatabase(self.base, self.section, self.school).create()
        self.tables = {"subject":self.subject, "course":self.course, "section":self.section, "rating":self.rating, "user":self.user, "school": self.school, "professor":self.professor}

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


    @contextmanager
    def _internal_scope(self, session=None):
        """
        Internal session manager that makes sure that the "correct" session is being used
        Will provide a session to the action, first tries to provide the session in the
            datbase object if that is availible (self.session), then tries a session passed
            in to the function, and finally creates a new session for the single action.
        In this way, it creates a few new sessions as possible and tries to prevent having
            multiple simultaneously active sessions
        """
        provided_session = None
        if self.session is not None:
            provided_session = self.session
        elif session is not None:
            provided_session = session
        else:
            provided_session = self.sessionmaker()

        try:
            yield provided_session
            provided_session.commit()
        except:
            provided_session.rollback()
            raise
        finally:
            provided_session.close()


    def new_school(self, name, abbreviataion, session=None):
        """
        creates a new school object for adding to the database
        """
        return self.school(school_name=name, school_short=abbreviataion)


    def new_user(self, username, email, password, school, admin=False, moderator=False, professor=False, session=None):
        """
        creates a new user object to be added to the database
        will throw errors
        """
        try:
            with self._internal_scope(session) as session:
                school_id = session.query(self.school).filter_by(school_short=school).one().school_id
        except sqlalchemy.orm.exc.NoResultFound:
            raise ItemDoesNotExistError(DatabaseObjects.School, school)

        query = {}
        query["password_salt"] = str(int(time.time()))
        query["password_hash"] = scrypt.hash(password, query["password_salt"], self.hashlength)
        query["apikey"] = hashlib.sha256(query["password_hash"]).hexdigest()
        query["school_id"] = school_id
        query["user_name"] = username
        query["email_address"] = email
        query["admin"] = admin
        query["moderator"] = moderator
        query["professor"] = professor

        return self.user(**query)


    def new_course(self, school, name, identifier, subject=None, session=None):
        """
        creates a new course with the given parameters
        this will throw errors
        """
        with self._internal_scope(session):
            try:
                school_id = session.query(self.school).filter_by(school_short=school).one().school_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)

            if subject is not None:
                try:
                    subject_id = session.query(self.subject).filter_by(name=subject).one().subject_id
                except sqlalchemy.orm.exc.NoResultFound:
                    raise ItemDoesNotExistError(DatabaseObjects.Subject, name)
            else:
                subject_id = None

        query = {}
        query["school_id"]=school_id
        query["course_name"]=name
        query["identifier"]=identifier
        query["subject"]=subject_id

        return self.course(**query)


    def new_section(self, school, course, professor=None, year=None, semester=None, session=None):
        """
        create a new section (subcourse) in the database
        will throw errors
        """
        with self._internal_scope(session):
            try:
                school_id = session.query(self.school).filter_by(school_short=school).one().school_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.School, school)

            try:
                course_id = session.query(self.course).filter_by(school_id=school_id, identifier=course).one().course_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.Course, course)

            if professor is not None:
                try:
                    professor_id = session.query(self.course).filter_by(name=professor).one().professor_id
                except:
                    raise ItemDoesNotExistError(DatabaseObjects.Professor, professor)
            else:
                professor_id = None

        query = {}
        query["parent_id"] = course_id
        query["professor_id"] = professor_id
        query["year"] = year
        query["semester"] = semester

        return self.section(**query)


    def new_subject(self, subject_name, session=None):
        """
        creates a new subject in the Database, short and sweet
        """
        return self.subject(subject_name=subject_name)


    def new_professor(self, name, bound_account=None, session=None):
        """
        adds a new professor to the dataabase
        """
        if bound_account is not None:
            with self._internal_scope(session):
                try:
                    user_id = session.query(self.user).filter_by(user_name=bound_account).one().user_id
                except sqlalchemy.orm.exc.NoResultFound:
                    raise ItemDoesNotExistError(DatabaseObjects.Professor, name)

        return self.professor(name=name, bound_account_id=user_id)


    def new_rating(self, user, course, professor=None, year=None, semester=None, rating=None, grade=None, rigor=None, utility=None, workload=None, difficulty=None, time=None, attendence=None, prof_rate=None, interactivty=None, session=None):
        """
        adds a new rating for a section by a user
        good lord this is suckish
        """
        with self._internal_scope(session):
            try:
                user = session.query(self.user).filter_by(user_name=user).one()
                school_name = user.school.school_short
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.User, user)

            try:
                school_id = session.query(self.school).filter_by(school_short=school_name).one().school_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.School, school_name)

            try:
                course_id = session.query(self.course).filter_by(school_id=school_id, identifier=course).one().course_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.Course, course)

            try:
                section_query = {}
                section_query["parent_id"] = course_id
                section_query["professor"] = professor
                section_query["year"] = year
                section_query["semester"] = semester
                section_id = session.query(self.session).filter_by(section_query).one().section_id
            except sqlalchemy.orm.exc.NoResultFound:
                raise ItemDoesNotExistError(DatabaseObjects.Section, course+str(semester)+" "+str(year))


        query = {}
        query["user_id"] = user.user_id
        query["section_id"] = section_id
        query["rating"] = rating
        query["grade"] = grade
        query["rigor"] = rigor
        query["utility"] = utility
        query["workload"] = workload
        query["difficulty"] = difficulty
        query["time"] = time
        query["attendence"] = attendence
        query["interactivty"] = interactivty
        query["professor"] = prof_rate

        return self.rating(query)
        

    def __iadd__(self, other):
        """
        syntactic sugar to add an item to the database with `db += other syntax`
        """
        if self.session is not None:
            self.session.add(other)
        else:
            with self.session_scope() as session:
                session.add(other)
        return self


    def item(self, table, *,  update=None, **kwargs):
        """
        utility function for use with the contains syntax
        """
        args = {}
        args["table"] = self.tables[table]
        args["query"] = kwargs
        args["update"] = update
        return args


    def __contains__(self, other):
        """
        syntactic sugar for checking if the database contains a given item using python's `x in y` syntax
        should generally be used along with Database.item()
        """
        with self._internal_scope(None) as session:
            return len(session.query(other["table"]).filter_by(**other["query"]).all()) > 0


    def __rshift__(self, other):
        """
        syntactic sugar for database updates.  Takes in an item
        `self.db >> db.item(users, update={dict},  id=5)`
        and updates it in the database
        """

        with self._internal_scope(None) as session:
            session.query(self.tables[other["table"]]).update().where(other["query"]).values(other["update"])

        return None


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
    This one contains information on the different types of objects in the database, for debugging outputs
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
    An ebum for the four semesters 
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


if __name__ == "__main__":
    db = Database(name="test.db")
    db.item(table="user", user_name="Admin") in db
    db += db.user(user_name="jmorton", email_address="josh@xephyr.us", password_hash="123", password_salt="123", apikey="123", admin=True, moderator=True)
    db.item(table="user", user_name="jmorton") in db
    db >> db.item("user", update={"first_name":"joshua"}, user_name="jmorton")