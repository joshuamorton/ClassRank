"""
"""

from tornado.web import RequestHandler, authenticated
from tornado.template import Template, Loader


class WelcomeHandler(RequestHandler):
    """
    """

    def get_current_user(self):
        return self.get_secure_cookie("user")

    @authenticated
    def get(self):
        print(self.get_secure_cookie("user"))
        self.render("welcome.html")
