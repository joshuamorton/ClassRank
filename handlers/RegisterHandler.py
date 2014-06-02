"""
"""
from tornado.web import RequestHandler
from tornado.template import Template, Loader
from handlers.settings import loader


class RegisterHandler(RequestHandler):
    """
    """
    def get(self):
        self.render("register.html")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        password2 = self.get_argument("password2", "")
        if username is not "":
            self.redirect("/login")
        else:
            self.redirect("/register")