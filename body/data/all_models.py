from flask_login import UserMixin
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, declared_attr
from werkzeug.security import generate_password_hash, check_password_hash

from body.helpers import URL


class CommonMixin:
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__


class Base(DeclarativeBase):
    pass


class RegisteredUser(Base, UserMixin, CommonMixin):
    id = Column(primary_key=True, autoincrement=True)
    nickname = Column(String)
    email = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    custom_pfp_extension = Column(String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @property
    def pfp_url(self):
        if self.custom_pfp_extension:
            return URL.for_pfp(self.id + '.' + self.custom_pfp_extension)
        return URL.for_img('default_pfp.png')

    @property
    def has_custom_pfp(self):
        return self.custom_pfp_extension is not None
