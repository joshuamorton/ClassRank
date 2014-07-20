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
from databases.database import Database

#todo: implement command line ioloop for, for example adding the first school and users (to create admins serverside)


global_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "autoreload":True,
    "template_path":os.path.join(os.path.dirname(__file__), "templates"),
    "login_url": "/login",
    "cookie_secret": "Hello world!"
    }
db = Database()
#a list of web routes and the objects to which they connect
class_rank = Application([
    (r'/', IndexHandler),
    (r'/index/?', IndexHandler),
    (r'/login/?', LoginHandler),
    (r'/register/?', RegisterHandler, dict(db=db)),
    (r'/logout/?', LogoutHandler),
    (r'/welcome/?', WelcomeHandler),
    (r'/app/?', AppHandler),
    ], **global_settings)

def runserver():
    #there will be multiple collaborative filter instances having to do with the different things
    class_rank.listen(8888)
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    if argv[1] == "runserver":
        runserver()