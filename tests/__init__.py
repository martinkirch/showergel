import logging
from unittest import TestCase

from webtest import TestApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bottle
from bottle.ext import sqlalchemy
from showergel import app, Base, rest
from showergel.liquidsoap_connector import Connection
# you may add echo=True :
__engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(__engine)
app.install(sqlalchemy.Plugin(__engine))

DBSession = sessionmaker(bind=__engine)

bottle.debug(mode=True)

Connection.setup()

class ShowergelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.getLogger().setLevel(logging.DEBUG)
        cls.app = TestApp(app)
