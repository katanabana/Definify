import os

from flask import Flask, render_template, redirect, url_for, send_from_directory
from flask_login import login_user
from public import current_user

from data.users import User
from forms import SignUpForm, SignInForm, EnterRoomForm, NicknameForm
from helpers import get_params, url_for_img, pfp_exists, get_path_to_pfp, get_extension
from rooms import Room
from global_ import rooms
from constants import HOST, PORT, UPLOAD_FOLDER
from keys import APPLICATION_KEY
from data.db_session import global_init, create_session
from events import connect_to_events
from login import configure_login

app = Flask(__name__)
app.config['SECRET_KEY'] = APPLICATION_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = connect_to_events(app)
configure_login(app)


@app.route('/pfp/<path:filename>')
def pfp(filename):
    return send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], 'pfp'), filename)


@app.route('/', methods=['POST', 'GET'])
def welcome():
    enter_room_form = EnterRoomForm()
    if enter_room_form.is_submitted():

        current_user.nickname = enter_room_form.nickname.data

        if enter_room_form.validate_on_set_pfp():
            if current_user.pfp != url_for_img('default_pfp.png') and pfp_exists(current_user.pfp):
                os.remove(get_path_to_pfp(current_user.pfp))  # remove previous profile picture
            file = enter_room_form.pfp.data
            filename = current_user.id + '.' + get_extension(file)
            pfp_url = url_for('pfp', filename=filename)
            file.save(get_path_to_pfp(pfp_url))
            current_user.pfp = pfp_url

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


@app.route('/match/<id_>', methods=['POST', 'GET'])
def match(id_):
    if id_ in rooms:
        nickname_form = NicknameForm()
        if nickname_form.validate_on_submit():
            current_user.nickname = nickname_form.nickname.data
        if current_user.nickname:
            return render_template('match.html', **get_params(room=rooms[id_]))
        return render_template('enter_nickname.html', **get_params(nickname_form=nickname_form))
    return render_template('room_not_found.html', **get_params())


if __name__ == '__main__':
    global_init('db/database.db')
    socketio.run(app, HOST, PORT, allow_unsafe_werkzeug=True)
