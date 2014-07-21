"""
"""
from tornado.web import RequestHandler, authenticated


class AdminpanelHandler(RequestHandler):
    """
    """
    def initialize(self, db):
        self.db = db

    @authenticated
    def get(self):
        self.render("adminpanel.html", **{"schools":self.db.schools, "users":self.db.users})

    @authenticated
    def post(self):
        school_name = str(self.get_argument("school_name", ""))
        school_short = str(self.get_argument("school_short", ""))
        with self.db.session_scope() as session:
            self.db.add_school(session, school_name, school_short)
        self.render("adminpanel.html", **{"schools":self.db.schools, "users": self.db.users})

    def get_current_user(self):
        return self.get_secure_cookie("user")