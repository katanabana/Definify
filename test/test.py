from random import randint
from flask_socketio import SocketIO

from flask import Flask, render_template, session
from flask_login import LoginManager, UserMixin, AnonymousUserMixin, current_user


class User:
    pass


class AuthenticatedUser(User, UserMixin):
    pass


class AnonymousUser(User, AnonymousUserMixin):
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sadfsadf'
login_manger = LoginManager(app)
login_manger.anonymous_user = AnonymousUser
socketio = SocketIO(app)


@login_manger.user_loader
def load_user(user_id):
    return AuthenticatedUser(user_id)


@app.route('/')
def root():
    return render_template('root.html')


@socketio.on('event')
def handle_event(data):
    print(data)


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
