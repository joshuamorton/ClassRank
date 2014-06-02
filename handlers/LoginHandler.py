"""
"""

from tornado.web import RequestHandler
from tornado.template import Template, Loader
from handlers.settings import loader
import tornado.escape


class LoginHandler(RequestHandler):
    """
    """

    def get(self):
        loader = Loader(self.get_template_path())
        self.write(loader.load("login.html").generate())

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")

        if self.is_authorized(username, password):
            self.authorize(username)
            print("redirecting to welcome")
        else:
            print("redirecting")
            self.redirect("/login")

    def is_authorized(self, username, password):
        if username == password:
            return True
        return False

    def authorize(self, user):
        if user:
            print("set cookie, ")
            print(tornado.escape.json_encode(user))
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.redirect("/welcome")
        else:
            print("cleared cookie")
            self.clear_cookie("user")
