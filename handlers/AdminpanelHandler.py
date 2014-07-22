"""
"""
from tornado.web import authenticated
from .BaseHandler import BaseHandler
import tornado


class AdminpanelHandler(BaseHandler):
    """
    """
    @authenticated
    def get(self):
        self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))

        with self.db.session_scope() as session:
            self.user = self.db.fetch_user_by_name(session, self.username)

        self.data = {"user":self.user, "auth":True}
        self.data["schools"] = self.db.schools
        self.data["users"] = self.db.users

        self.render("adminpanel.html", **self.data)


    @authenticated
    def post(self):
        self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        with self.db.session_scope() as session:
            self.user = self.db.fetch_user_by_name(session, self.username)
        self.data["user"] = self.user
        
        school_name = str(self.get_argument("school_name", ""))
        school_short = str(self.get_argument("school_short", ""))
        
        with self.db.session_scope() as session:
            self.db.add_school(session, school_name, school_short)
        self.data = {"user":self.user, "auth":True}
        self.data["schools"] = self.db.schools
        self.data["users"] = self.db.users
        
        self.render("adminpanel.html", **self.data)

    
