from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, ValidationError

from constants import HOST, PORT, ALLOWED_EXTENSIONS
from data.db_session import create_session
from data.users import User
from global_ import rooms
from helpers import get_extension


class MyForm(FlaskForm):
    def __init__(self):
        # prefix is added because it allows to create multiple forms with same names of fields
        # without getting same names and ids in html file after rendering template
        super().__init__(prefix=self.__class__.__name__)

    def is_submitted(self):
        # FlaskForm is considered submitted if there is an active post request.
        # Because of that is_submitted of all forms on a page returns True
        # even when only one form was actually submitted.
        # After redefining form is considered to be submitted
        # only if its submit field has value True
        for field in self:
            if type(field) is SubmitField and field.data:
                return super().is_submitted()
        return False


class SignUpForm(MyForm):
    username = StringField('Username', [DataRequired()])
    email = EmailField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        return

    def validate_email(self, email):
        if not create_session().query(User).filter(User.email == email.data).first():
            return
        raise ValidationError('An account with this email already exists.')


class SignInForm(MyForm):
    email = EmailField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')

    def __init__(self):
        super().__init__()
        self.user = create_session().query(User).filter(User.email == self.email.data).first()

    def validate_email(self, _):
        if self.user:
            return
        raise ValidationError('User with such email does not exist.')

    def validate_password(self, password):
        if self.user:
            if self.user.check_password(password.data):
                return
            raise ValidationError('Wrong password for user with such email.')
        # if user doesn't exist no password error will be raised


def url_validator(_, link):
    if link.data:
        parts = link.data.split('/')
        if len(parts) == 3 and parts[0] in [f'{HOST}:{PORT}', ''] and parts[1] == 'match':
            if parts[-1] in rooms:
                return
            raise ValidationError('There is no such room.')
        raise ValidationError('Link is not valid.')
    raise ValidationError('Enter the link to join the room.')


def pfp_validator(_, pfp_field):
    file = pfp_field.data
    # check if the post request has the file part
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file and file.filename:
        if get_extension(file) in ALLOWED_EXTENSIONS:
            return
        raise ValidationError('File has an extension that is not allowed.')
    raise ValidationError('Choose a file to set it as the profile picture.')


class NicknameForm(FlaskForm):
    nickname = StringField(validators=[DataRequired('Enter your nickname to enter the room.')])


class EnterRoomForm(NicknameForm):
    join = SubmitField('Join')
    create = SubmitField('Create')
    url = StringField()
    pfp = FileField()

    def validate_on_set_pfp(self):
        return self.validate({'pfp': [pfp_validator]})

    def validate_on_join(self):
        return self.join.data and self.validate({'url': [url_validator]})

    def validate_on_create(self):
        return self.create.data and self.validate()
