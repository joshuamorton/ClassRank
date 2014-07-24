"""
"""
from tornado.web import authenticated
from .BaseHandler import BaseHandler


class AdminpanelHandler(BaseHandler):
    """
    """
    @authenticated
    def get(self):
        self.get_user_obj()

        self.data["auth"] = True
        self.data["schools"] = self.db.schools
        #this I would consider the blackest of magicks
        with self.db.session_scope() as session:
            for school in self.data["schools"]:
                session.add(school)
                school.numcourses = len(school.courses)
                school.numstudents = len(school.students)
        self.data["users"] = self.db.users
        self.data["user"] = self.user

        self.render("adminpanel.html", **self.data)


    @authenticated
    def post(self):
        self.get_user_obj()
        
        school_name = str(self.get_argument("school_name", ""))
        school_short = str(self.get_argument("school_short", ""))
        
        with self.db.session_scope() as session:
            self.db.add_school(session, school_name, school_short)
            self.data = {"user":self.user, "auth":True, "session":session}
            self.data["schools"] = self.db.schools
            self.data["users"] = self.db.users

            self.render("adminpanel.html", **self.data)
