from flask import session
from flask_login import LoginManager, AnonymousUserMixin

from data.db_session import create_db_session
from helpers import get_random_string, URL

class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        super().__init__()
        self.nickname = session.get('nickname', '')
        self.id = session.get('id', get_random_string())
        self.pfp_url = session.get('pfp', URL.for_img('default_pfp.png'))

    def __setattr__(self, key, value):
        session[key] = value

    def __getattr__(self, item):
        return session.get(item)

    def get_id(self):
        return self.id


def configure_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        return create_db_session().query(User).get(user_id)
