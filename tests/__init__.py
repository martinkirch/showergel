from unittest import TestCase
from webtest import TestApp
from sqlalchemy import create_engine
import bottle
from bottle.ext import sqlalchemy
from showergel import app, Base

class ShowergelTestCase(TestCase):

    def tearDown(self):
        self.app.reset()

    @classmethod
    def setUpClass(cls):
        from showergel import rest

        # you may add echo=True :
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        app.install(sqlalchemy.Plugin(engine))
        
        bottle.debug(mode=True)
        cls.app = TestApp(app)
