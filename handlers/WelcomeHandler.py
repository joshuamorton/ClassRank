"""
"""

from tornado.web import RequestHandler, authenticated


class WelcomeHandler(RequestHandler):
    """
    """

    def get_current_user(self):
        return self.get_secure_cookie("user")

    @authenticated
    def get(self):
        print(self.get_secure_cookie("user"))
        self.render("welcome.html")
