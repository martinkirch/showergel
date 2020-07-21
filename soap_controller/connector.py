import logging
from telnetlib import Telnet

log = logging.getLogger(__name__)

class Connector:
    """
    Wraps the telnet connection and commands, including a mutex so threads wait
    for their turn to send their command
    """
    ENCODING = 'ascii'

    def __init__(self, host, port):
        self.telnet = Telnet(host, port)

    def close(self):
        self.telnet.close()

    def send(self, command):
        """
        Send `command`, returns its response.
        TODO : mutex this
        """
        log.debug("SEND: %s", command)
        self.telnet.write(command.encode(self.ENCODING) + b"\n")
        answer = self.telnet.read_until(b"END")
        answer = answer[0:-3].decode(self.ENCODING).strip()
        log.debug("RECEIVE: %s", answer)
        return answer
