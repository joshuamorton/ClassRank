"""
"""

from tornado.web import RequestHandler
from tornado.template import Template, Loader


class IndexHandler(RequestHandler):
    """
    """
    def get(self):
        loader = Loader(self.get_template_path())
        self.render("splash.html")
