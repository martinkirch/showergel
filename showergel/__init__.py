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
from functools import wraps
from datetime import datetime

from bottle import Bottle, response, HTTPError, request
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
        response.content_type = 'application/json'
        if (res.exception and
            isinstance(res.exception, json.JSONDecodeError) and
            "request.json" in res.traceback
            ):
            response.status = 400
            return json.dumps({"code": 400, "message": "Please send well-formed JSON"})
        else:
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

    def force_python_rootlogger(fn):
        """
        PaserServer's logger may bypasses our logging.config.fileConfig,
        especially when an error occurs. So we add this tiny plugin
        """
        @wraps(fn)
        def _force_python_rootlogger(*args, **kwargs):
            try:
                actual_response = fn(*args, **kwargs)
            except HTTPError:
                raise
            except Exception as excn:
                _log.exception(excn)
                raise HTTPError(500, "Internal Error", excn) from None
            return actual_response
        return _force_python_rootlogger
    app.install(force_python_rootlogger)

    debug = bool(app.config['listen'].get('debug'))

    app.run(
        server='paste',
        host=app.config['listen']['address'],
        port=int(app.config['listen']['port']),
        reloader=debug,
        quiet=True,
    )
