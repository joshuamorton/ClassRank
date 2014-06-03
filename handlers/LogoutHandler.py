"""
"""

from tornado.web import RequestHandler
from tornado.template import Template, Loader


class LogoutHandler(RequestHandler):
    """
    """
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")
