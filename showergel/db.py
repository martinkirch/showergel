"""

"""
from typing import Type
from configparser import ConfigParser

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class SessionContext(object):
    """
    A context manager providing an SQLAlchemy session where foreign key
    constraints are enabled. Before exiting the context, it commits (or
    rollback in case of exception) the transaction and closes the session.

    The first call to ``SessionContext()`` **must** provide a ``config`` object.
    """
    engine = None
    _session_maker = None

    def __init__(self, config:Type[ConfigParser]=None):
        if SessionContext._session_maker is None:
            SessionContext.engine = engine_from_config(config['db'])
            SessionContext._session_maker = sessionmaker(bind=SessionContext.engine)
        self.session = SessionContext._session_maker()
        self.session.execute("PRAGMA foreign_keys = ON")

    def __enter__(self) -> Type[Session]:
        return self.session

    def __exit__(self, type, value, traceback):
        if type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()
