"""
=========
Showergel
=========
"""

import logging
import json
from datetime import datetime

from bottle import Bottle, response, HTTPError, request, static_file, redirect, HTTPResponse
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from bottle.ext.sqlalchemy import Plugin as SQLAlchemyPlugin

_log = logging.getLogger(__name__)
Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class ShowergelBottle(Bottle):

    def default_error_handler(self, res):
        response.content_type = 'application/json'
        if (res.exception and
            isinstance(res.exception, json.JSONDecodeError) and
            "request.json" in res.traceback
            ):
            response.status = 400
            return json.dumps({"code": 400, "message": "Please send well-formed JSON"})
        else:
            return json.dumps({"code": int(res.status_code), "message": res.body})
    
    def get_engine(self):
        for p in self.plugins:
            if isinstance(p, SQLAlchemyPlugin):
                return p.engine
        return None

app = ShowergelBottle()
from . import rest
