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
            self.data["your_ratings"] = {course.course_id : self.db.fetch_rating_by_id(self, session, self.data["user"].user_id, course.course_id) for course in self.data["your_courses"]}
        self.render("dash.html", **self.data)

