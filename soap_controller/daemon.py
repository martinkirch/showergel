"""
Invoke::

    soap_controller_daemon path_to_daemon.ini

"""

import os
import sys
import socketserver
import threading
import logging
import logging.config
from configparser import ConfigParser

_log = logging.getLogger(__name__)


class SoapHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.rfile.readline().decode("utf8").strip()
            except UnicodeDecodeError:
                break
            if not data:
                break
            cur_thread = threading.current_thread()
            response = f"{os.getpid()}#{cur_thread.name}: {data.upper()}".encode("utf8")
            self.wfile.write(response)


class SoapServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def server_activate(self):
        _log.info("SoapServer listening %r", self.server_address)
        super().server_activate()


def main():
    if len(sys.argv) < 2:
        print("Missing argument: path to daemon.ini", file=sys.stderr)
        sys.exit(1)
    conf = ConfigParser()
    conf.read(sys.argv[1])
    logging.config.fileConfig(sys.argv[1], disable_existing_loggers=False)

    server_conf = (conf['listen']['address'], int(conf['listen']['port']))
    server = SoapServer(server_conf, SoapHandler)
    server.serve_forever()
