
import unittest
import os
import database
import sqlalchemy.ext
import scrypt



class DatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            os.remove("./data/Testdb.db")
        except FileNotFoundError as e:
            pass

    def setUp(self):
        """
        instantiates the test database
        """
        self.db = database.Database(name="Testdb.db", folder="data")

    def test_01_remove(self):
        """
        tests creating and deleting an empty database
        """
        self.assertTrue(self.db)
        with self.db.session_scope() as session:
            #you can operate on an empty database
            self.assertFalse(self.db.school_exists(session, school_short="Georgia Tech"))

        os.remove("./data/Testdb.db")  # hard remove the database file (this should never happen)
        self.assertTrue(self.db)
        with self.db.session_scope() as session:
            #when the database doesn't exist, shit breaks yo
            self.assertRaises(sqlalchemy.exc.OperationalError, self.db.school_exists, session, {"school_short":"Georgia Tech"})

    def test_02_add_schools(self):
        #establish a connection
        with self.db.session_scope() as session:
            self.assertFalse(self.db.school_exists(session, "Georgia Tech"))
        
        #establish another connection 
        #this tests that connections are created/ended correctly 
        with self.db.session_scope() as session:
            #make some schools to use later
            self.db.add_school(session, school_name="Georgia Institute of Technology", school_identifier="Georgia Tech")
            self.db.add_school(session, school_name="Harvard University", school_identifier="Harvard")
            self.db.add_school(session, school_name="This is a hilariously long name that is longer than anything in productin !@#$%^&*()_+", school_identifier="!@#$%^&*()_+ also way longer than anything irl")

        with self.db.session_scope() as session:
            #check that the fetch_school and school_exists work
            self.assertTrue(self.db.school_exists(session, school_name="Georgia Institute of Technology"))
            self.assertTrue(self.db.school_exists(session, school_short="Georgia Tech"))
            self.assertTrue(self.db.school_exists(session, school_id=3))
            self.assertEqual(self.db.fetch_school_by_name(session, "Georgia Tech").school_name, "Georgia Institute of Technology")
            self.assertEqual(self.db.fetch_school_by_id(session, 1).school_name, "Georgia Institute of Technology")
            self.assertRaises(database.ItemDoesNotExistError, self.db.fetch_school_by_name, session, "help me")

    def test_03_add_users(self):
        with self.db.session_scope() as session:
            self.assertFalse(self.db.user_exists(session, "jmorton"))

        with self.db.session_scope() as session:
            #shows that a complex user can be added
            self.assertTrue(self.db.add_user(session, "jmorton", "joshua.morton@gatech.edu", "password", "Georgia Tech", first="Joshua", last="Morton", admin=True, mod=True))
            #as well as a simple one
            self.db.add_user(session, "cmalan", "malanMan@harvard.edu", "CS50isTheBest", "Harvard", mod=True)
            #but that they need to attend a real school
            self.assertFalse(self.db.add_user(session, "fake_user", "fmail", "fake_pw", "fakeuni"))

        with self.db.session_scope() as session:
            #checks that users can be searched
            self.assertTrue(self.db.user_exists(session, user_name="jmorton"))
            self.assertTrue(self.db.user_exists(session, email_address="malanMan@harvard.edu"))
            self.assertTrue(self.db.user_exists(session, user_id=1))
            #shows that even when correct information from conflicting users is provided, the result is correct
            self.assertFalse(self.db.user_exists(session, user_name="jmorton", email_address="malanMan@harvard.edu"))
            self.assertEqual(self.db.fetch_user_by_name(session, "jmorton").first_name, "Joshua")
            #and nonexistant users throw errors
            self.assertRaises(database.ItemDoesNotExistError, self.db.fetch_user_by_name, session, "name")
            #hashes are not the same as passwords
            self.assertNotEqual(self.db.fetch_user_by_name(session, "jmorton").password_hash, "password")
            #and we can authenticate users from them
            tempuser = self.db.fetch_user_by_name(session, "jmorton")
            self.assertEqual(tempuser.password_hash, scrypt.hash("password", tempuser.password_salt, self.db.hashlength))

    def test_04_add_courses(self):
        with self.db.session_scope() as session:
            self.assertFalse(self.db.course_exists(session, coursename="CS1301"))

        with self.db.session_scope() as session:
            #you can add a course
            self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301")
            #and a similar one that is more complex
            self.assertTrue(self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Fall.value))
            self.assertFalse(self.db.course_exists(session, school="Georgia Tech", coursename="CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))
            #and similar courses differing only in semester
            self.assertTrue(self.db.add_course(session, "Georgia Tech", "Introduction to Computer Science in Python", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))

        with self.db.session_scope() as session:
            #two courses that are similar are not the same
            self.assertNotEqual(self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Fall.value), 
                self.db.fetch_course_by_name(session, "Georgia Tech", "CS1301", professor="Summet", year=2013, semester=database.Semesters.Spring.value))
            #and furthermore, there are more than 2 couses, meaning things are different
            self.assertGreater(len(self.db.courses), 2)
            

    def test_05_add_ratings(self):
        pass

    def test_06_updates(self):
        pass

    def test_07_deletes(self):
        pass

    def test_08_misc(self):
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)

