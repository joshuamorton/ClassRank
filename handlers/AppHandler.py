"""
"""

from tornado.web import RequestHandler, authenticated
from tornado.template import Template, Loader

class AppHandler(RequestHandler):
    """
    """
    def initialize(self, difficulties):
        """
        Adds a collaborative filter object to the app under the name self.filter
        """
        pass
        
    def get_current_user(self):
        return self.get_secure_cookie("user")

    @authenticated
    def get(self):
        self.render("app_main.html")
