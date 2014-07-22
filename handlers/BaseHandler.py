"""
"""
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    """
    """
    def get_current_user(self):
        return self.get_secure_cookie("user")


    def initialize(self, db):
        self.db = db
        self.data = {"auth":False, "user":None}
