from .BaseSocket import BaseSocket
from tornado.escape import json_decode, json_encode

class ApiToggleSocket(BaseSocket):
    """
    """
    def open(self):
        pass

    def on_message(self, message):
        data = json_decode(message)
        self.user = self.get_user_obj(data["username"])
        if self.is_authenticated(data["username"], data["apikey"]):
            with self.db.session_scope() as session:
                toggled_user = self.db.fetch_user_by_id(session, data["toggled"])
                if data["role"] == "moderator" and any([self.user.moderator, self.user.admin]):
                    toggled_user.moderator = not toggled_user.moderator
                elif data["role"] == "admin" and data["username"] != toggled_user.user_name and self.user.admin:
                    toggled_user.admin = not toggled_user.admin
            self.write_message(json_encode({"status":"toggled"}))
        else:
            self.write_message(json_encode({"status":"failed"}))