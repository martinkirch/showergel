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
from configparser import ConfigParser
from functools import wraps

from bottle import Bottle, response, HTTPError, request, static_file, redirect, HTTPResponse
from bottle.ext.sqlalchemy import Plugin as SQLAlchemyPlugin
from sqlalchemy import engine_from_config

from showergel.showergel_bottle import ShowergelBottle
from showergel.rest import sub_apps
from showergel.liquidsoap_connector import Connection

_log = logging.getLogger(__name__)


def force_python_rootlogger(fn):
    """
    Server's logger may bypasses our logging.config.fileConfig,
    especially when an error occurs. So we add this tiny plugin
    """
    @wraps(fn)
    def _force_python_rootlogger(*args, **kwargs):
        try:
            actual_response = fn(*args, **kwargs)
        except HTTPError:
            raise
        except Exception as excn:
            if isinstance(excn, HTTPResponse):
                # may happen when redirecting: Bottle raises a response
                return excn
            else:
                _log.exception(excn)
                raise HTTPError(500, "Internal Error", excn) from None
        return actual_response
    return _force_python_rootlogger

def send_cors(fn):
    """
    Send CORS headers along all requests.
    This is only enabled in debug mode, because WebPack's live-compiling-server
    is hosting on another port
    """
    @wraps(fn)
    def _send_cors(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, HEAD, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            return fn(*args, **kwargs)
    return _send_cors


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
        self.install(force_python_rootlogger)
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
        for sub_app in sub_apps:
            sub_app.config = self.config

        engine = engine_from_config(self.config['db'])
        self.install(SQLAlchemyPlugin(engine))

        if demo:
            self.install(send_cors)
            from showergel.demo import stub_all
            stub_all(self.get_engine(), self.config)
        elif debug:
            _log.warning("Running in development mode - don't do this on a broadcasting machine")
            self.install(send_cors)

        Connection.setup(self.config)

    def install(self, plugin):
        """
        Because Bottle.install does not install plug-ins to sub-applications
        """
        super().install(plugin)
        for sub_app in sub_apps:
            sub_app.install(plugin)

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


def read_bool_param(param):
    value = app.config['listen'].get(param)
    if value in ('False', 'false'):
        return False
    else:
        return bool(value)

def serve():
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

    try:
        port = int(app.config['listen']['port'])
    except ValueError:
        port = int(environ[app.config['listen']['port']])

    demo = read_bool_param('demo')
    debug = read_bool_param('debug')
    server = 'paste'
    if demo:
        # stubbing to :memory: works better with the default, mono-threaded server
        server = 'wsgiref'
    app.run(
        server=server,
        host=app.config['listen']['address'],
        port=port,
        reloader=debug,
        quiet=True,
        demo=demo,
        debug=debug,
    )

if __name__ == '__main__':
    serve()
