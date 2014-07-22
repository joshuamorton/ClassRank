"""
The base class from which most (all? other handlers will inherit)
"""
from tornado.web import RequestHandler
import tornado


class BaseHandler(RequestHandler):
    """
    """
    def get_current_user(self):
        """
        An override to the builtin @authenticate, can be rewritten to be better
            if eventually necessary
        """
        return self.get_secure_cookie("user")


    def initialize(self, db):
        """
        Gives the handler some base information that it can then change
        """
        if self.get_secure_cookie("user"):
            self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        self.db = db
        self.data = {"auth":False, "user":None}

    def get_user_obj(self):
        self.username = tornado.escape.json_decode(self.get_secure_cookie("user"))
        with self.db.session_scope() as session:
            self.user = self.db.fetch_user_by_name(session, self.username)
        return self.user

    #do not override get_template_namespace()