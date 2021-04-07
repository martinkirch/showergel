import logging
from unittest import TestCase

from webtest import TestApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bottle
from bottle.ext import sqlalchemy

from showergel import app
from showergel.db import Base
from showergel.liquidsoap_connector import Connection

app.config = {
    'db': {
        "sqlalchemy.url": "sqlite:///:memory:",
        "echo": True,
    },
    'interface': {
        'name': "ShowergelTest",
    }
}
app.init()

__engine = app.get_engine()
Base.metadata.create_all(__engine)
DBSession = sessionmaker(bind=__engine)

bottle.debug(mode=True)

class ShowergelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.getLogger().setLevel(logging.DEBUG)
        cls.app = TestApp(app)
