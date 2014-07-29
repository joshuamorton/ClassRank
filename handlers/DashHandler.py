"""
"""

from tornado.web import authenticated
from .BaseHandler import BaseHandler

class DashHandler(BaseHandler):
    """
    """
    
    @authenticated
    def get(self):
        self.data["user"] = self.get_user_obj()
        self.data["auth"] = True
        with self.db.session_scope() as session:
            self.data["school_courses"] = self.db.fetch_school_by_id(session, self.user.school_id).courses
            session.add(self.user)
            self.data["your_courses"] = self.user.courses
        self.render("dash.html", **self.data)

