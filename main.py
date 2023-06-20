import os
from os.path import isdir

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_login import login_user

from body.current import Current
from body.data.all_models import RegisteredUser
from body.data.data import Data
from body.forms import SignUpForm, SignInForm, EnterRoomForm, NicknameForm
from body.helpers import get_extension, URL, post_get
from body.rooms import Room
from body.global_ import rooms
from body.data.db_session import create_db_session, init_data
from body.events import connect_to_events
from body.login import configure_login

app = Flask(__name__)
load_dotenv()
app.config['UPLOAD_FOLDER'] = os.getenv('DATA_DIRECTORY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = connect_to_events(app)
configure_login(app)


@app.context_processor
def context():
    return dict(URL=URL)


@app.route('/pfp/<path:filename>')
def pfp(filename):
    return send_from_directory(Data.pfp, filename)


@app.route('/', **post_get)
def welcome():
    enter_room_form = EnterRoomForm()
    if enter_room_form.is_submitted():

        Current.user.nickname = enter_room_form.nickname.data

        if enter_room_form.validate_on_set_pfp():
            if Current.user.has_custom_pfp and isdir(Current.user.pfp_url):
                os.remove(Current.user.pfp_url)  # remove previous profile picture
            file = enter_room_form.pfp.data
            Current.user.pfp_extension = get_extension(file)
            file.save(Current.user.pfp_url)

        if enter_room_form.validate_on_join():
            return redirect(enter_room_form.url.data)

        elif enter_room_form.validate_on_create():
            room = Room(socketio)
            rooms[room.id] = room
            return redirect(url_for('match', id_=room.id))

    sign_up_form = SignUpForm()
    if sign_up_form.validate_on_submit():
        user = User()
        user.nickname = sign_up_form.username.data
        user.email = sign_up_form.email.data
        user.set_password(sign_up_form.password.data)
        sess = create_session()
        sess.add(user)
        sess.commit()

    sign_in_form = SignInForm()
    if sign_in_form.validate_on_submit():
        login_user(sign_in_form.user, remember=sign_in_form.remember)

    params = get_params({
        'enter_room_form': enter_room_form,
        'sign_up_form': sign_up_form,
        'sign_in_form': sign_in_form,
        'pfp': 'default_pfp.png'
    })
    return render_template('welcome.html', **params)


@app.route('/match/<id_>', *post_get)
def match(id_):
    if id_ in rooms:
        nickname_form = NicknameForm()
        if nickname_form.validate_on_submit():
            Current.user.nickname = nickname_form.nickname.data
        if Current.user.nickname:
            return render_template('match.html', **get_params(room=rooms[id_]))
        return render_template('enter_nickname.html', **get_params(nickname_form=nickname_form))
    return render_template('room_not_found.html', **get_params())


if __name__ == '__main__':
    init_data()
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    socketio.run(app, host, port, allow_unsafe_werkzeug=True)
