import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from body.data.all_models import Base


class Data:
    root = os.getenv('DATA_DIRECTORY')
    pfp = os.path.join(root, 'pfp')
    db = os.path.join(root, 'db')
    get_db_session = None

    def __init__(self):
        if not os.path.isdir(self.root):
            os.mkdir(self.root)
        os.mkdir(self.root)

        conn_str = f'sqlite:///{self.db}?check_same_thread=False'
        engine = create_engine(conn_str, echo=False)
        self.get_db_session = sessionmaker(engine)
        Base.metadata.create_all(engine)