"""
==============
Soapbox Daemon
==============

This is actually a RESTful HTTP server holding SQLite databases.

Launch by invoking::

    soapbox_daemon path_to_daemon.ini

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
import logging
import logging.config
import json
from typing import Type
import pkg_resources

from configparser import ConfigParser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from .metadata import save_metadata

_log = logging.getLogger(__name__)


def get_config() -> ConfigParser:
    """
    Parses ``sys.argv`` to find the config file's path.
    Does some basic configuration, and return a loaded ``ConfigParser``.
    """
    if len(sys.argv) < 2:
        print("Missing argument: path to daemon.ini", file=sys.stderr)
        sys.exit(1)
    conf = ConfigParser()
    conf.read(sys.argv[1])
    logging.config.fileConfig(sys.argv[1], disable_existing_loggers=False)
    return conf


def _handle_exception(f):
    """
    decorator for ``SoapboxHandler```methods, catching any Exception.
    Exceptions are logged, then the handler replies ``500 Internal Error``.
    """
    def wrapper(*args):
        try:
            f(*args)
        except Exception as exc:
            _self = args[0]
            _log.exception(exc)
            _self.send_response(500)
            _self.end_headers()
    return wrapper

class SoapboxHandler(BaseHTTPRequestHandler):
    server_version = "SoapboxServer/" + pkg_resources.get_distribution("soapbox").version

    def _close(self, code):
        self.send_response(code)
        self.end_headers()

    @_handle_exception
    def do_GET(self):
        self._close(200)

    @_handle_exception
    def do_POST(self):
        length = int(self.headers.get('content-length'))
        raw = self.rfile.read(length).decode('utf8', errors='replace')
        data = json.loads(raw)
        self.rfile.close()
        _log.debug("POST %s got %r", self.path, data)

        if self.path == "/metadata_log":
            save_metadata(self.server.config, data)
        else:
            self._close(404)
            return

        self._close(200)

    def log_message(self, *args):
        "Override the super method to redirect messages to our own log"
        _log.info(*args)


class SoapboxServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, config:Type[ConfigParser], handler_class):
        self.config = config
        super().__init__(
            (config['listen']['address'], int(config['listen']['port'])),
            handler_class
        )

    def server_activate(self):
        _log.info("SoapboxServer listening %r", self.server_address)
        super().server_activate()


def main():
    with SoapboxServer(get_config(), SoapboxHandler) as server:
        server.serve_forever()
