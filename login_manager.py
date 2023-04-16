from flask import session
from flask_login import LoginManager, AnonymousUserMixin

from data.db_session import create_session
from data.users import User
from helpers import get_random_string


class AnonymousUser(AnonymousUserMixin):
    @property
    def nickname(self):
        return session.get('nickname', '')

    @nickname.setter
    def nickname(self, value):
        session['nickname'] = value
    @property
    def id(self):
        return self.get_id()

    def get_id(self):
        id_ = session.get('id', None)
        if id_:
            return id_
        id_ = get_random_string()
        session['id'] = id_
        return id_


def configure_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = create_session()
        return db_sess.query(User).get(user_id)
