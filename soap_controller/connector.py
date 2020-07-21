import logging
from telnetlib import Telnet

import gi
from gi.repository import Gtk

log = logging.getLogger(__name__)

class Connector:
    """
    Wraps the telnet connection and commands, including a mutex so threads wait
    for their turn to send their command.

    It also drives the "console panel" of the application.
    """
    ENCODING = 'ascii'

    def __init__(self, host: str, port: int, builder: Gtk.Builder):
        self.telnet = Telnet(host, port)
        self.buffer = builder.get_object("console_buffer")
        # see https://stackoverflow.com/questions/58165694/scroll-to-bottom-of-scrollable-if-content-changes-in-python-gtk
        self.text_mark_end = self.buffer.create_mark("", self.buffer.get_end_iter(), False)
        self.scrolled_window = builder.get_object("console_scrolled_window")
        self.view = builder.get_object("console_view")
        self.entry = builder.get_object("console_entry")

        builder.connect_signals({
            'do_console_command': self.do_command
        })

    def close(self):
        self.telnet.close()

    def do_command(self, target: Gtk.Entry):
        command = target.get_text().strip()
        if command:
            self.send(command)
        target.set_text('')

    def send(self, command: str) -> str:
        """
        Send `command`, returns its response.
        TODO : mutex this
        """
        log.debug("SEND: %s", command)
        self.buffer.insert(self.buffer.get_end_iter(), "--> %s\n" % command)
        self.telnet.write(command.encode(self.ENCODING) + b"\n")
        answer = self.telnet.read_until(b"END")
        answer = answer[0:-3].decode(self.ENCODING).strip()
        log.debug("RECEIVE: %s", answer)
        self.buffer.insert(self.buffer.get_end_iter(), answer + "\n")
        self.view.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)
        return answer
