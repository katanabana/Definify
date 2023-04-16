from flask import Flask, render_template, redirect, request, session
from flask_login import login_user
from public import current_user

from data.users import User
from forms import PfpForm, SignUpForm, SignInForm, JoinForm, CreateForm, NicknameForm
from helpers import get_params
from rooms import Room
from global_ import rooms
from secret_keys import APPLICATION_KEY, API_KEY
from data.db_session import global_init, create_session
from events import connect_to_events
from login_manager import configure_login

app = Flask(__name__)
app.config['SECRET_KEY'] = APPLICATION_KEY
socketio = connect_to_events(app)
configure_login(app)


@app.route('/', methods=['POST', 'GET'])
def welcome():
    nickname_form = NicknameForm()
    join_form = JoinForm()
    create_form = CreateForm()

    if join_form.is_submitted():
        nickname_form.action = 'join'
        nickname_form.validate()
        print(nickname_form.nickname.data)
        current_user.nickname = nickname_form.nickname.data

    if create_form.is_submitted():
        nickname_form.action = 'create'
        nickname_form.validate()
        current_user.nickname = nickname_form.nickname.data

    if join_form.validate_on_submit():
        return redirect(join_form.link.data)

    if create_form.validate_on_submit():
        room = Room()
        rooms[room.id] = room
        return redirect(f'/match/{room.id}')

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
        'create_form': create_form,
        'join_form': join_form,
        'sign_up_form': sign_up_form,
        'sign_in_form': sign_in_form,
        'pfp': 'default_pfp.png',
        'pfp_form': PfpForm(),
        'user': current_user,
        'nickname_form': nickname_form
    })
    return render_template('welcome.html', **params)


@app.route('/match/<id_>', methods=['POST', 'GET'])
def match(id_):
    if current_user.nickname:
        if id_ in rooms:
            return render_template('match.html', **get_params())
        return render_template('enter_nickname.html', **get_params())
    return render_template('room_not_found.html', **get_params())


if __name__ == '__main__':
    global_init('db/database.db')
    socketio.run(app, allow_unsafe_werkzeug=True)
