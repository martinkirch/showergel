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

import bottle
from bottle.ext import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config


Base = declarative_base()
app = bottle.Bottle()
_log = logging.getLogger(__name__)
WWW_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www")


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

    app.run( # TODO use debug, server, reloader
        host=app.config['listen']['address'],
        port=int(app.config['listen']['port']),
        # reloader=True,
        # debug=True,
    )
