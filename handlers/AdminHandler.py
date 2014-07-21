"""
"""
from tornado.web import RequestHandler
import tornado
import scrypt


class AdminHandler(RequestHandler):
    """
    """
    def initialize(self, db):
        self.db = db

    def get(self):
        self.render("adminlogin.html")

    def post(self):
        username = str(self.get_argument("username", ""))
        password = str(self.get_argument("password", ""))

        #print("username = "+username+" password = "+password) #dat security

        if username == "jmorton" and scrypt.hash(password, username, 64) == b"\x9fq&_pc\x13E\\\xa2\xf7+BQ\x80\xdf\xb4\x98\xe7\ri'\xb0\xd3)\x7fKq\xd4>\x1f\x91\x04@u\x1b\xd4t\x0089_47k\x00T+\xedWx\x8c\xe9\x1e\x887\x11\xf2T\xb6=\xde\xbc\x0f":
            self.authorize(username)

    def authorize(self, user):
        if user:
            print("set cookie, ")
            #print(tornado.escape.json_encode(user))
            #self.set_current_user(user)
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            print("redirecting to adminpanel")
            self.redirect("/adminpanel")
        else:
            print("cleared cookie")
            self.clear_cookie("user")