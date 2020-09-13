"""
Installed as soap_controller_daemon

"""

import os
import socketserver
import threading
import logging

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

def main():
    server = SoapServer(("localhost", 4321), SoapHandler)
    server.serve_forever()
