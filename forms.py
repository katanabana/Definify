from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, ValidationError

from data.db_session import create_session
from data.users import User
from global_ import rooms


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


class PfpForm(MyForm):
    file = FileField([FileRequired()])


class JoinForm(MyForm):
    join = SubmitField('Join')
    url = StringField()

    def validate_url(self, link):
        if link.data:
            parts = link.data.split('/')
            if len(parts) == 3 and parts[0] == '' and parts[1] == 'match':
                if parts[-1] in rooms:
                    return
                raise ValidationError('There is no such room.')
            raise ValidationError('Link is not valid.')
        raise ValidationError('Enter the link to join the room.')


class CreateForm(MyForm):
    create = SubmitField('Create')

    def validate_create(self, _):
        if current_user.nickname:
            return
        raise ValidationError('Enter your nickname to create room.')


class NicknameForm(FlaskForm):
    nickname = StringField()

    def validate_nickname(self, action):
        if current_user.nickname:
            pass
        raise ValidationError(f'Enter your nickname to {self.action} the room.')



