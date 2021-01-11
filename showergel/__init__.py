"""
=========
Showergel
=========
"""

import sys
import os.path
import logging
import logging.config
import json
from configparser import ConfigParser

from bottle import Bottle, response, HTTPError
from bottle.ext import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config, event

_log = logging.getLogger(__name__)
Base = declarative_base()
WWW_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class ShowergelBottle(Bottle):

    def default_error_handler(self, res):
        if isinstance(res, HTTPError):
            _log.critical("Uncaught %r", res.exception)
            _log.critical(res.traceback)
        response.content_type = 'application/json'
        return json.dumps({"code": int(res.status_code), "message": res.body})

app = ShowergelBottle()

def main():
    if len(sys.argv) < 2:
        print("Missing argument: path to showergel's .ini", file=sys.stderr)
        sys.exit(1)
    config_path = sys.argv[1]
    logging.config.fileConfig(config_path, disable_existing_loggers=False)
    
    # we don't use Bottle's app.config.load_config because it's eager loading
    # values: that doesn't go well with interpolation keys in logging config
    parser = ConfigParser()
    parser.read(config_path)
    app.config = parser
    
    engine = engine_from_config(app.config['db'])
    app.install(sqlalchemy.Plugin(engine))

    from . import rest

    debug = bool(app.config['listen'].get('debug'))

    app.run(
        server='paste',
        host=app.config['listen']['address'],
        port=int(app.config['listen']['port']),
        reloader=debug,
        debug=debug,
    )
