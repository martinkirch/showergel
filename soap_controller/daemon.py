"""

test with::

    systemd-socket-activate -l 4321 python3 soap_controller/daemon.py


see also
 - https://github.com/torfsen/python-systemd-tutorial

"""

import os
import socket
import threading
import socketserver

import systemd.daemon

import logging

_log = logging.getLogger(__name__)


class SoapHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().decode("utf8").strip()
        cur_thread = threading.current_thread()
        response = f"{os.getpid()}#{cur_thread.name}: {self.data.upper()}".encode("utf8")
        self.wfile.write(response)


class SoapServer(socketserver.ThreadingMixIn, socketserver.BaseServer):
    def __init__(self, fd):
        self.socket = socket.socket(fileno=fd)

        if not systemd.daemon.is_socket(self.socket):
            raise ConnectionError(f'file descriptor {fd} is not a systemd socket')

        self.listening = systemd.daemon.is_socket(self.socket, listening=1)

        systemd.daemon.notify('READY=1')

        super().__init__(self.socket.getsockname(), SoapHandler)

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        if self.listening:
            r = self.socket.accept()
            return r
        else:
            # socket has already been accepted by systemd
            return self.socket, self.socket.getpeername()

def listen_server() -> SoapServer:
    fds = systemd.daemon.listen_fds(True)
    if len(fds) > 1:
        raise ValueError("Unexpected : we have more than on file descriptor")

    return SoapServer(fds[0])


if __name__ == '__main__':
    server = listen_server()
    server.serve_forever()
