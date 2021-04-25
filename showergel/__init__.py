"""
=========
Showergel
=========
"""

from os import environ
import os.path
import sys
import logging
import logging.config
import json
from functools import wraps

import toml
import click
from bottle import Bottle, response, HTTPError, request, static_file, redirect, HTTPResponse
from bottle.ext.sqlalchemy import Plugin as SQLAlchemyPlugin
from sqlalchemy import engine_from_config

from showergel.showergel_bottle import ShowergelBottle
from showergel.rest import sub_apps
from showergel.liquidsoap_connector import Connection

_log = logging.getLogger(__name__)


def send_cors():
    """
    Send CORS headers along all requests.
    This is only enabled in debug mode, because WebPack's live-compiling-server
    is hosting on another port
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, HEAD, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


class MainBottle(ShowergelBottle):

    def run(self, **kwargs):
        """
        Bottle's auto-reloader runs the main app in two processes :
        when activated, we ensure the initialization in only performed by
        the child (reloading) process.

        Also note that this function is _not_ called when running unit tests,
        but ``init`` is called.

        http://bottlepy.org/docs/dev/tutorial.html#auto-reloading
        """
        if not kwargs['reloader'] or environ.get('BOTTLE_CHILD'):
            self.init(demo=kwargs['demo'], debug=kwargs['debug'])
        elif kwargs['reloader']:
            _log.info("Showergel starting with auto reloader...")
        del kwargs['demo']
        super().run(**kwargs)

    def init(self, demo=False, debug=False):
        """
        Showergel's initialization function
        """
        engine = engine_from_config(self.config, prefix="db.sqlalchemy.")
        plugin = SQLAlchemyPlugin(engine)
        self.install(plugin)
        for sub_app in sub_apps:
            sub_app.install(plugin)
            sub_app.config.update(self.config)

        if demo:
            self.add_hook('after_request', send_cors)
            from showergel.demo import stub_all
            stub_all(self.get_engine(), self.config)
        elif debug:
            _log.warning("Running in development mode - don't do this on a broadcasting machine")
            self.add_hook('after_request', send_cors)

        Connection.setup(self.config)

    def get_engine(self):
        for p in self.plugins:
            if isinstance(p, SQLAlchemyPlugin):
                return p.engine
        return None


app = MainBottle()
for sub in sub_apps:
    app.merge(sub)

static_root = os.path.join(os.path.dirname(__file__), 'www')
@app.route('/<path:path>')
def serve_front(path):
    return static_file(path, root=static_root)

@app.route('/')
def root_redirect():
    redirect('/index.html')

@app.route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
    """
    this only ensures we support ``OPTIONS`` requests (instead of returning 405).
    CORS headers will be returned iff ``send_cors`` is enabled.
    """
    return {}

def read_bool_param(param):
    value = app.config.get('listen.'+param)
    if value in ('False', 'false'):
        return False
    else:
        return bool(value)

@click.command()
@click.version_option()
@click.argument('config_path', type=click.Path(readable=True, allow_dash=False, exists=True))
@click.option('--verbose', is_flag=True, help="Sets logging level to DEBUG")
def serve(config_path, verbose):
    with open(config_path, 'r') as f:
        conf = toml.load(f)
    logging.config.dictConfig(conf['logging'])
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    app.config.load_dict(conf)

    try:
        port = int(app.config['listen.port'])
    except ValueError:
        port = int(environ[app.config['listen.port']])

    demo = read_bool_param('demo')
    debug = read_bool_param('debug')
    server = 'paste'
    if demo:
        # stubbing to :memory: works better with the default, mono-threaded server
        server = 'wsgiref'
    app.run(
        server=server,
        host=app.config['listen.address'],
        port=port,
        reloader=debug,
        quiet=True,
        demo=demo,
        debug=debug,
    )

if __name__ == '__main__':
    serve()
