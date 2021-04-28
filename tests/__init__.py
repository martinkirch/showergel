import logging
import sys
from unittest import TestCase

from webtest import TestApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bottle
from bottle.ext import sqlalchemy

from showergel import app
from showergel.db import Base
from showergel.liquidsoap_connector import Connection

APP_CONFIG = {
    'db.sqlalchemy': {
        "url": "sqlite:///:memory:",
        # "echo": True,
    },
    'interface': {
        'name': "ShowergelTest",
    },
    'metadata_log': {
        'extra_fields': ["track*"],
    }
}
app.config.load_dict(APP_CONFIG)
app.init()

__engine = app.get_engine()
Base.metadata.create_all(__engine)
DBSession = sessionmaker(bind=__engine)

bottle.debug(mode=True)

logging.basicConfig(
    format="%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s] %(message)s",
    level=logging.DEBUG,
)

class ShowergelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = TestApp(app)
