"""
"""

from tornado.web import authenticated
from .BaseHandler import BaseHandler

class SettingsHandler(BaseHandler):
    """
    """
        
    @authenticated
    def get(self):
        self.data["auth"] = True
        self.data["user"] = self.get_user_obj()

        self.render("settings.html", **self.data)

    @authenticated
    def post(self):
        #get args
        first_name = self.get_argument("fname", default=None, strip=True)
        last_name = self.get_argument("lname", default=None, strip=True)
        email = self.get_argument("email", default=None, strip=True)
        age = int(self.get_argument("age", default=0, strip=True))
        grad = int(self.get_argument("grad", default=0, strip=True))
        if age == 0:
            age = None
        if grad == 0:
            grad = None

        with self.db.session_scope() as session:
            self.db.update_user(session, self.username, first=first_name, last=last_name, email_address=email, age=age, graduation=grad)



        self.data["auth"] = True
        self.data["user"] = self.get_user_obj()

        self.render("settings.html", **self.data)



    def get_template_namespace(self):
        #This is a bit of a hack, but it works
        namespace = BaseHandler.get_template_namespace(self)

        def fetch_school(school):
            with self.db.session_scope() as session:
                 return self.db.fetch_school_by_id(session, school)

        namespace = dict(fetch_school=fetch_school,**namespace)
        namespace.update(self.ui)
        return namespace

