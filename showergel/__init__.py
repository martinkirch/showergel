"""
=========
Showergel
=========
"""

from os import environ
import os.path
import logging
import logging.config
from functools import wraps

from bottle import response, request, static_file, redirect
from bottle.ext.sqlalchemy import Plugin as SQLAlchemyPlugin
from sqlalchemy import engine_from_config
from sqlalchemy.pool import StaticPool

from showergel.showergel_bottle import ShowergelBottle
from showergel.rest import sub_apps
from showergel.liquidsoap_connector import Connection
from showergel.scheduler import Scheduler

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
        store_scheduler_in_memory = demo
        if ":memory:" in self.config['db.sqlalchemy.url']: # unit tests !
            store_scheduler_in_memory = True
            # see https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
            engine = engine_from_config(self.config,
                prefix="db.sqlalchemy.",
                connect_args={'check_same_thread':False},
                poolclass=StaticPool
            )
        else:
            engine = engine_from_config(self.config, prefix="db.sqlalchemy.")
        plugin = SQLAlchemyPlugin(engine)
        self.install(plugin)
        for sub_app in sub_apps:
            sub_app.install(plugin)
            sub_app.config.update(self.config)

        Scheduler.setup(engine, store_in_memory=store_scheduler_in_memory)

        if demo:
            self.add_hook('after_request', send_cors)
            from showergel.demo import stub_all
            stub_all(engine, self.config)
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
