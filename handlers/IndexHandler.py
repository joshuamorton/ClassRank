"""
"""

from tornado.web import RequestHandler
from tornado.template import Template, Loader
from handlers.settings import loader


class IndexHandler(RequestHandler):
    """
    """
    def get(self):
        loader = Loader(self.get_template_path())
        self.write(loader.load("splash.html").generate())
