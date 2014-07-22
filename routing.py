#!/usr/bin/python3
"""
"""

import os
from tornado import ioloop
from tornado.web import Application
from sys import argv
#there must be a better way to do this!
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

from databases.database import Database


#todo: implement command line ioloop for, for example adding the first school and users (to create admins serverside)


global_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "autoreload":True,
    "template_path":os.path.join(os.path.dirname(__file__), "templates"),
    "login_url": "/login",
    "cookie_secret": "Hello world!"
    }

#the gloabl database
db = Database()

#a list of web routes and the objects to which they connect
class_rank = Application([
    (r'/', IndexHandler),
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
    (r'/api/?', AppHandler, dict(db=db)),
    ], **global_settings)

def runserver():
    #there will be multiple collaborative filter instances having to do with the different things
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