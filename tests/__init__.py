import logging
from unittest import TestCase

from webtest import TestApp
from sqlalchemy.orm import sessionmaker
import bottle
from bottle.ext import sqlalchemy

from showergel import app
from showergel.db import Base
from showergel.metadata import Log, LogExtra

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
    },
    'cartfolders': {
        'testcart': '/tmp/TBA',
    },
    'liquidsoap': {
        'cartfolders_queue': 'stubbedqueue',
    },
}
app.config.load_dict(APP_CONFIG)
app.init(conf=APP_CONFIG)

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        session = DBSession()
        session.query(LogExtra).delete(synchronize_session=False)
        session.query(Log).delete(synchronize_session=False)
        session.commit()
