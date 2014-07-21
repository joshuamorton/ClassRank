"""
"""
from tornado.web import RequestHandler


class RegisterHandler(RequestHandler):
    """
    """
    def initialize(self, db):
        self.db = db

    def get(self):
        self.render("register.html")

    def post(self):
        username = self.get_argument("username", "")
        email = self.get_argument("email", "")
        school = self.get_argument("school", "")
        password = self.get_argument("password", "")
        password2 = self.get_argument("password2", "")

        if username != "" and email != "" and password == password2 and school != "" and len(password) < 256:
            with self.db.session_scope() as session:
                self.db.add_user(session, username, email, password, school)
            self.redirect("/login")
        else:
            self.redirect("/register")
