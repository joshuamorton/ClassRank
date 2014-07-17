
import unittest
import os
import database
import sqlalchemy.ext

"""
session_scope ->
    connect
    disconnect
fetch_school_by_name ->

fetch_course_by_name ->

fetch_user_by_name ->

fetch_rating_by_name ->

fetch_school_by_id ->

fetch_user_by_id ->

fetch_course_by_id ->

fetch_rating_by_id ->

school_exists ->
    works when false
    called with school_name
    works when true
    called with school_id
course_exists ->
    works when false
    called with coursename
user_exists ->
    works for false
    called with username
rating_exists ->
    
add_school ->
    works for values
add_rating ->

add_course ->

add_user ->

remove_user ->

remove_rating ->

update_rating ->

update_course ->

update_user ->

"""


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        """
        instantiates the test database
        """
        self.db = database.Database(name="Testdb.db", folder="data")

    def test_create(self):
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

    def test_add_schools(self):
        """
        tests adding to the database 
        """
        with self.db.session_scope() as session:
            self.assertFalse(self.db.school_exists(session, school_short="Georgia Tech"))
            self.db.add_school(session, school_name="Georgia Institute of Technology", school_identifier="Georgia Tech")
            self.db.add_school(session, school_name="Harvard University", school_identifier="Harvard")
            self.db.add_school(session, school_name="This is a terribly long name that would never appear in production and has !@#$%^&*(): weird characters" , school_identifier="its identifier is also terribly long")

if __name__ == "__main__":
    unittest.main()

