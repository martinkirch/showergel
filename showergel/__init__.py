"""
==============
Showergel Daemon
==============

This is actually a RESTful HTTP server for a SQLite database.

Launch by invoking::

    showergel config.ini

This module acts as our Web framework.
In its main class ``ShowergelHandler``,
functions ``do_GET`` and ``do_POST`` are our router functions,
actually implemented in other modules.

GET requests:
=============

Parameters are expected bundled in a query string (``application/x-www-form-urlencoded``),
response is JSON.

``/metadata_log``
-----------------

Return an array of logged metadata.
Possible parameters:

  * ``chronological`` may be set to anything non-empty (use ``1`` or ``true``),
    otherwise results are sorted recent first.
    Doesn't affect the interpretation of ``start`` and ``end``.
  * log interval, as ``start`` and ``end`` (inclusive).
    For example ``start=2020-12-01 12:00:00&end=2020-12-01 14:00:00``.
  * if ``start`` or ``end`` is missing, ``limit`` restricts the number of results (and defaults to 10).

Therefore, ``GET /metadata_log`` returns the 10 most recent metadata items played.

POST requests:
==============

All ``POST`` requests should attach their data as JSON.

``/metadata_log``
-----------------

Save Liquidsoap's metadata, it can be called from Liquidsoap by::

    def post_to_daemon(m)
        response = http.post("http://localhost:4321/metadata_log", data=json_of(m))
        log(label="http_posted", string_of(response))
    end

    radio = on_metadata(post_to_daemon, source)

"""

import sys
import os.path
import logging
import logging.config
import json
from typing import Type
import pkg_resources

from configparser import ConfigParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from .db import SessionContext
from .metadata import save_metadata, Log

_log = logging.getLogger(__name__)
WWW_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "www")


def get_config(path=None) -> ConfigParser:
    """
    If provided ``path`` is ``None``, parses ``sys.argv`` to find the config file's path.
    Does some basic configuration, and return a loaded ``ConfigParser``.
    """
    if path is None:
        if len(sys.argv) < 2:
            print("Missing argument: path to showergel's .ini", file=sys.stderr)
            sys.exit(1)
        path = sys.argv[1]
    config = ConfigParser()
    config.read(path)
    logging.config.fileConfig(path, disable_existing_loggers=False)
    return config


def _showergel_wrapper(f):
    """
    decorator for ``ShowergelHandler```methods, providing self.db (a fresh
    SQLAlchemy session), self.query (for GET), cleaned self.path and catching any Exception.
    Exceptions are logged, then the handler replies ``500 Internal Error``.
    """
    def wrapper(*args):
        _self = args[0]
        try:
            with SessionContext() as session:
                _self.db = session
                parsed = urlparse(_self.path)
                _self.path = parsed.path

                _self.query = parse_qs(parsed.query)
                for k, v in _self.query.items():
                    _self.query[k] = v[0]

                f(*args)
        except Exception as exc:
            _log.exception(exc)
            _self.send_response(500)
            _self.end_headers()
    return wrapper

class ShowergelHandler(SimpleHTTPRequestHandler):
    server_version = "ShowergelServer/" + pkg_resources.get_distribution("showergel").version

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server, directory=WWW_ROOT)

        # those will be set by _showergel_wrapper later
        self.db = None
        self.query = None

    def version_string(self):
        """
        Overridden because the default implem also reveals Python version
        """
        return self.server_version

    def _close(self, code):
        self.send_response(code)
        self.end_headers()

    def _json_response(self, serializable):
        self.log_request(200)
        self.send_response_only(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(serializable).encode('utf8'))

    @_showergel_wrapper
    def do_GET(self):
        if self.path == "/metadata_log":
            self._json_response(Log.get(self.db,
                start=self.query.get('start'),
                end=self.query.get('end'),
                limit=self.query.get('limit'),
                chronological=self.query.get('chronological')
            ))
        else:
            super().do_GET()

    @_showergel_wrapper
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        raw = self.rfile.read(length).decode('utf8', errors='replace')
        data = json.loads(raw)
        self.rfile.close()
        _log.debug("POST %s got %r", self.path, data)

        if self.path == "/metadata_log":
            save_metadata(self.server.config, self.db, data)
        else:
            self._close(404)
            return

        self._close(200)

    def log_message(self, *args):
        "Override the super method to redirect messages to our own log"
        _log.info(*args)


class ShowergelServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, config:Type[ConfigParser], handler_class):
        self.config = config
        SessionContext(config=config)
        super().__init__(
            (config['listen']['address'], int(config['listen']['port'])),
            handler_class
        )

    def server_activate(self):
        _log.info("ShowergelServer listening http://%s:%d/",
            self.server_address[0], self.server_address[1])
        super().server_activate()


def main():
    with ShowergelServer(get_config(), ShowergelHandler) as server:
        server.serve_forever()
