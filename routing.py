#!/usr/bin/python3
"""
"""

import os
from tornado import ioloop
from tornado.web import Application
from sys import argv
# there must be a better way to do this!
from handlers.IndexHandler import IndexHandler
from handlers.RegisterHandler import RegisterHandler
from handlers.LoginHandler import LoginHandler
from handlers.LogoutHandler import LogoutHandler
from handlers.WelcomeHandler import WelcomeHandler
from handlers.AppHandler import AppHandler
from handlers.AdminpanelHandler import AdminpanelHandler
from handlers.DashHandler import DashHandler
from handlers.SettingsHandler import SettingsHandler
from handlers.ModHandler import ModHandler
from api.handlers.ApiHome import ApiHome
from api.handlers.ApiSchool import ApiSchool
from api.handlers.ApiSchools import ApiSchools
from api.handlers.ApiUsers import ApiUsers
from api.handlers.ApiUser import ApiUser
from api.handlers.ApiToggleMod import ApiToggleMod
from api.handlers.ApiToggleAdmin import ApiToggleAdmin


from databases.database import Database


global_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "autoreload": True,
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "login_url": "/login",
    "cookie_secret": "Hello world!"
    }

# the gloabl database
db = Database()

# a list of web routes and the objects to which they connect
class_rank = Application([
    (r'/', IndexHandler, dict(db=db)),
    (r'/index/?', IndexHandler, dict(db=db)),
    (r'/login/?', LoginHandler, dict(db=db)),
    (r'/register/?', RegisterHandler, dict(db=db)),
    (r'/logout/?', LogoutHandler, dict(db=db)),
    (r'/welcome/?', WelcomeHandler, dict(db=db)),
    (r'/app/?', AppHandler, dict(db=db)),
    (r'/adminpanel/?', AdminpanelHandler, dict(db=db)),
    (r'/dashboard/?', DashHandler, dict(db=db)),
    (r'/modpanel/?', ModHandler, dict(db=db)),
    (r'/settings/?', SettingsHandler, dict(db=db)),
    # catches the following:
    #     /api/school/123
    #     /api/school/123
    #     /api/school/Georgia_Tech
    #     /api/school/123/
    #     /api/school/Georgia_Tech.json
    (r'/api/school/(.+?)(?:/?|(?:\.json)?)', ApiSchool, dict(db=db)),
    # catches the following:
    #     /api/schools
    #     /api/schools/
    #     /api/schools.json
    (r'/api/schools(:?/|\.json)?', ApiSchools, dict(db=db)),
    # catches the following:
    #     /api/user/123
    #     /api/user/jmorton
    #     /api/user/123/
    #     /api/jmorton.json
    (r'/api/user/(.+?)(?:/?|(?:\.json)?)', ApiUser, dict(db=db)),
    # catches the following:
    #     /api/schools
    #     /api/schools/
    #     /api/schools.json
    (r'/api/users(:?/|\.json)?', ApiUsers, dict(db=db)),
    (r'/api/toggle/admin/(\d+)/?', ApiToggleAdmin, dict(db=db)),
    (r'/api/toggle/moderator/(\d+)/?', ApiToggleMod, dict(db=db)),

    (r'/api/?', ApiHome, dict(db=db)),
    # user/(#####)
    # school/(#####)
    # course/(#####)/(#####)
    # user/user_name
    # school/school_abbr
    # course/school_abbr/(#####)
    # course/school_abbr/course_abbr
    # adminpanel/schools
    # adminpanel/users
    # adminpanel/courses
    # adminpanel/school/(#####)
    # adminpanel/user/(#####)
    # adminpanel/course/(#####)/(#####)
    ], **global_settings)


def runserver():
    # there will be multiple collaborative filter instances having to do with the different things
    class_rank.listen(8888)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    if argv[1] == "runserver":
        runserver()
    if argv[1] == "add_school":
        with db.session_scope() as session:
            db.add_school(session, argv[2], argv[3])
    if argv[1] == "admin":
        with db.session_scope() as session:
            db.update_user(session, argv[2], admin=True)
