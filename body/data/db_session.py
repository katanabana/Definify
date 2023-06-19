import os.path

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

from body.data.data import Data

SqlAlchemyBase = dec.declarative_base()

__factory = None


def init_data():
    global __factory

    if __factory:
        return

    if not os.path.isdir(Data.root):
        os.mkdir(Data.root)
    os.mkdir(Data.root)
    conn_str = f'sqlite:///{path}?check_same_thread=False'

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
