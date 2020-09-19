import logging
import os
import sys
import pkg_resources

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Gio, GObject

from .connector import Connector

log = logging.getLogger(__name__)

_version = pkg_resources.get_distribution("soapbox").version

class SoapboxGUI(Gtk.Application):
    __gsignals__ = {
        'connect': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, *args, **kwargs):
        Gtk.Application.__init__(self,
                                 *args,
                                 application_id="org.soapbox",
                                 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                 **kwargs)
        self.builder = None
        self.window = None
        self.host = None
        self.port = 1234
        self.connection = None

        self._command_line_options()

    def _command_line_options(self):
        """
        Those are actually processed by `do_command_line`_.
        """
        self.add_main_option("verbose", ord("v"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Show debugging messages in the console",
            None,
        )
        self.add_main_option("host", ord("h"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "Hostname running the Liquidsoap instance",
            None,
        )
        self.add_main_option("port", ord("p"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.INT,
            "Liquidsoap server's port number",
            None,
        )

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # more GTK plumbing can go here

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            glade_source = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "main.glade"
            )
            self.builder = Gtk.Builder()
            self.builder.add_from_file(glade_source)

            self.window = self.builder.get_object("main_window")
            self.window.set_title("Soapbox %s" % _version)
            self.window.set_application(self)
            self.window.show_all()

            self.builder.connect_signals({
                'do_connection_response': self.do_connection_response,
            })

            if self.host:
                self.emit("connect")
            else:
                dialog = self.builder.get_object("connection_dialog")
                dialog.run()

        self.window.present()

    def do_command_line(self, command_line):
        """
        Process command line options, and configures logging (to stderr).
        """
        options = command_line.get_options_dict()
        options = options.end().unpack()

        log_level = logging.WARNING
        if "verbose" in options:
            log_level = logging.DEBUG
        logging.basicConfig(stream=sys.stderr, level=log_level,
            # maybe add %(thread)d ?
            format='%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s')
        log.info("Starting SoapboxGUI %s", _version)

        if "host" in options:
            self.host = options["host"]
        if "port" in options:
            self.port = options["port"]

        self.activate()
        return 0

    def status_message(self, message):
        """
        Prints a message in the main window's status bar
        """
        statusbar = self.builder.get_object("statusbar")
        statusbar.remove_all(0)
        statusbar.push(0, message)

    def do_connect(self, host=None, port=None):
        if host:
            self.host = host
        if port:
            self.port = port
        self.status_message("Connecting to %s:%d..." % (self.host, self.port))
        try:
            self.connection = Connector(self.host, self.port, self.builder)
            self.connection.send("help")
            self.status_message("Connected to %s:%d" % (self.host, self.port))
        except Exception as caught:
            self.status_message(str(caught))
            raise

    def do_connection_response(self, target, response=None):
        """
        "Connect to" dialog response. target can be the dialog itself,
        the entry inside, or one of the two buttons
        """
        dialog = self.builder.get_object("connection_dialog")
        entry = self.builder.get_object("connection_entry")

        if response in (Gtk.ResponseType.DELETE_EVENT, Gtk.ResponseType.CANCEL):
            response = Gtk.ResponseType.CANCEL
        elif response == Gtk.ResponseType.OK:
            pass
        elif target == entry or target.get_label()=='gtk-connect':
            response = Gtk.ResponseType.OK
        else:
            response = Gtk.ResponseType.CANCEL

        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            self.quit()

        if response == Gtk.ResponseType.OK:
            raw = entry.get_text().strip()
            if raw:
                splitted = raw.split(":")
                if len(splitted) == 1:
                    self.host = splitted[0].strip()
                elif len(splitted) == 2:
                    try:
                        self.port = int(splitted[1])
                    except ValueError:
                        log.warning("%s is not a port number", splitted[1])
                        return
                    self.host = splitted[0].strip()

        if self.host:
            dialog.destroy()
            self.emit("connect")

    def do_shutdown(self):
        logging.debug("do_shutdown called")
        Gtk.Application.do_shutdown(self)
        if self.connection:
            self.connection.close()

def main():
    app = SoapboxGUI()
    app.run(sys.argv)
