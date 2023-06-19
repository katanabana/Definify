from flask_login import UserMixin
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, declared_attr
from werkzeug.security import generate_password_hash, check_password_hash


class CommonMixin:
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__


class Base(DeclarativeBase):
    pass


class User(CommonMixin, Base, UserMixin):
    id = Column(primary_key=True, autoincrement=True)
    nickname = Column(String)
    email = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    pfp_extension = Column(String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
