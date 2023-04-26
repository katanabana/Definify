import os

from flask import session
from flask_login import LoginManager, AnonymousUserMixin

from constants import UPLOAD_FOLDER
from data.db_session import create_session
from data.users import User
from helpers import get_random_string, url_for_img, pfp_exists


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        super().__init__()
        self.nickname = session.get('nickname', '')
        self.id = session.get('id', get_random_string())
        self.pfp = session.get('pfp')
        if not (self.pfp and pfp_exists(self.pfp)):
            self.pfp = url_for_img('default_pfp.png')

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        session[key] = value

    def get_id(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id


def configure_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = create_session()
        return db_sess.query(User).get(user_id)
