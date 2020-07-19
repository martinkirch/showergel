import logging
import os
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Gio

from . import __version__


class SoapController(Gtk.Application):
    def __init__(self, *args, **kwargs):
        Gtk.Application.__init__(self,
                                 *args,
                                 application_id="org.soap-controller",
                                 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                 **kwargs)
        self.builder = None
        self.window = None
        self.host = None
        self.port = 1234

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
            self.window.set_title("Soap Controller %s" % __version__)
            self.window.set_application(self)
            self.window.show_all()

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
        logging.info("Starting Liguidsoap %s", __version__)

        if "host" in options:
            self.host = options["host"]
        if "port" in options:
            self.port = options["port"]

        self.activate()
        return 0

def main():
    app = SoapController()
    app.run(sys.argv)
