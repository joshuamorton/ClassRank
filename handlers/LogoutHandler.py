"""
"""

from tornado.web import RequestHandler
from tornado.template import Template, Loader
from handlers.settings import loader


class LogoutHandler(RequestHandler):
    """
    """
    def get(self):
        self.clear_cookie("user")
        loader = Loader(self.get_template_path())
        self.redirect("/login")
