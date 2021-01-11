import logging
from unittest import TestCase

from webtest import TestApp
from sqlalchemy import create_engine
import bottle
from bottle.ext import sqlalchemy
from showergel import app, Base, rest

# you may add echo=True :
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
app.install(sqlalchemy.Plugin(engine))

bottle.debug(mode=True)

class ShowergelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.getLogger().setLevel(logging.DEBUG)
        cls.app = TestApp(app)
