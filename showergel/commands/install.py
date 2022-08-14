"""
Showergel interactive installer

see the ``install`` section of the README file.
"""

import logging
import os
import os.path
import shutil
import socket

import click
import toml
from sqlalchemy import engine_from_config

from .main import showergel_cli


_log = logging.getLogger(__name__)

TOML_TEMPLATE = """
[db.sqlalchemy]
url = "sqlite:///{db}"

[interface]
# name displayed in the interface's left bar
name = "{basename}"

############### Metadata logger ###############
[metadata_log]

# list of metadata fields that should be stored when available, in addition to
# artist/title/album. You can use * to represent any characters or nothing.
# For example, "track*" will include "track" but also "track_number" or "tracktotal"
extra_fields = [
    "genre",
    "year",
]

############## Server configuration ##########
[listen]
# Showergel's interface will be available at http://[address]:[port]/
# As there is no security check, be careful to keep the address on a private network.
# If port is not a number, we assume it is the name of an environment variable
# that contains the required port number (like, Heroku's $PORT).
address = "localhost"
port = {port:d}
{debug}

############## Liquidsoap connection #########
[liquidsoap]

# Parameters enabling Showergel's link to Liquidsoap. Those are necessary to
# display "now playing" information, or for scheduling.
# If your Liquidsoap script contains the following settings:
#
# settings.server.telnet.set(true)
# settings.server.telnet.bind_addr.set("127.0.0.1")
# settings.server.telnet.port.set(1234)
#
# then change "method" from "none" to "telnet".

method = "none"
host = "127.0.0.1"
port = 1234

############# Logging configuration ##########
[logging]
version = 1
disable_existing_loggers = false

[logging.formatters.generic]
format = "%(asctime)s %(levelname)-5.5s [%(process)d][%(threadName)s][%(name)s:%(lineno)s] %(message)s"

[logging.handlers.main]
formatter = "generic"
{handler}

[logging.root]
level = "{log_level}"
handlers = ["main"]

"""

LIQUID_UNIT_TEMPLATE = """
[Unit]
Description={basename} Liquidsoap daemon
After=network.target

[Service]
Type=forking
PIDFile={pid_path}
WorkingDirectory={base_dir}
ExecStart={liquidsoap_binary} {run_script}
Restart=always

[Install]
WantedBy=default.target
"""

LIQUID_TEMPLATE = """
#!{liquidsoap_binary}

settings.log.file.set(true)
settings.log.file.path.set("{log_path}")
settings.init.daemon.set(true)
settings.init.daemon.pidfile.set(true)
settings.init.daemon.pidfile.path.set("{pid_path}")
%include "{liq_path}"
"""

SHOWERGEL_UNIT_TEMPLATE = """
[Unit]
Description={basename} Showergel daemon
After=network.target

[Service]
Type=simple
Restart=always
WorkingDirectory={base_dir}
ExecStart={showergel} serve {toml_path}

[Install]
WantedBy=default.target
"""


class Installer(object):
    def __init__(self):
        self.basename = 'radio'
        self.port = 2345
        self.liquid_service_name = None
        self.service_name = None
        self.enabled = False

        home = os.environ.get('HOME')
        if not home:
            raise click.ClickException("Cannot find HOME environment variable")
        self.path_systemd_units = home + "/.config/systemd/user/"

    @property
    def path_toml(self):
        return os.getcwd() + '/' + self.basename + '.toml'

    @property
    def path_db(self):
        return os.getcwd() + '/' + self.basename + '.db'

    @property
    def path_log(self):
        if self.liquid_service_name:
            return os.getcwd() + '/' + self.basename + '_gel.log'
        else:
            return os.getcwd() + '/' + self.basename + '.log'

    def _potential_paths(self):
        for path in [
            self.path_toml,
            self.path_db,
            self.path_log,
            os.getcwd() + '/' + self.basename + '_gel.log',
            os.getcwd() + '/' + self.basename + '_soap.liq',
            self.path_systemd_units + self.basename + '.service',
            self.path_systemd_units + self.basename + '_gel.service',
            self.path_systemd_units + self.basename + '_soap.service',
            ]:
            yield path

    def revert(self):
        for path in self._potential_paths():
            if os.path.exists(path):
                os.unlink(path)

    def hello(self):
        click.secho("Welcome to showergel installer !",
            fg='green', bold=True)
        click.echo("\nWe will ask for a few parameters.\n\nWhen in doubt, just press Enter and we'll use the default value (shown between square brackets).\nHit Ctlr+C to abort.")

    def ask_basename(self):
        click.secho("\nHow should we call the installation ?", bold=True)
        click.echo("We need a simple name (use only letters and numbers) for the future files and service.")
        while True:
            basename = click.prompt("Installation basename", default=self.basename)
            if basename.isalnum():
                self.basename = basename
                break
            else:
                click.secho("Use only letters and numbers", color='red')

    def ask_port(self):
        click.echo("\nWhich port should we use for Showergel's interface ? Just ensure nothing else is already using it.")
        while True:
            port = click.prompt("Showergel port", default=self.port, type=int)
            if self.port_is_open(port):
                click.secho(f"Port {port} is already held by another application, please pick another one.", fg='red')
            else:
                if port < 1024:
                    click.secho("Warning: showergel will run as a normal user, it will unlikely be able to open a port below 1024", fg='yellow')
                self.port = port
                return

    def port_is_open(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = (0 == sock.connect_ex(('localhost', port)))
        sock.close()
        return result

    def check_no_overwriting(self):
        for path in self._potential_paths():
            if os.path.exists(path):
                raise click.ClickException(f"{path} already exists, which suggests that Showergel is already installed. Or maybe install with another basename.")

    def create_toml_and_db(self, dev=False):
        if dev:
            handler = 'class = "rich.logging.RichHandler"'
            debug = "debug = true"
            log_level = "DEBUG"
        else:
            handler = """class = "logging.handlers.RotatingFileHandler"
filename = "{}"
maxBytes = 10000000
backupCount = 10
""".format(self.path_log)
            debug = ""
            log_level = "INFO"
        with open(self.path_toml, 'w') as toml_file:
            click.echo("Writing configuration file: "+self.path_toml)
            toml_file.write(TOML_TEMPLATE.format(
                db=self.path_db,
                port=self.port,
                handler=handler,
                debug=debug,
                log_level=log_level,
                basename=self.basename,
            ))
        click.echo("Initializing database: "+self.path_db)
        self.create_db_schema()

    def create_db_schema(self, path_toml=None):
        if not path_toml:
            path_toml = self.path_toml

        from showergel.db import Base
        # indirectly import all Base subclasses:
        from showergel import rest

        with open(path_toml, 'r') as f:
            config = toml.load(f)
        engine = engine_from_config(config['db']['sqlalchemy'], prefix='')
        Base.metadata.create_all(engine)

    def ask_liquid_script(self):
        click.echo("\nIf you would like to also create a systemd service for your Liquidsoap script, enter its path below. Otherwise, leave blank.")
        while True:
            liq = click.prompt("Path to Liquidsoap script (absolute or relative)", default="")
            if liq:
                if not liq.startswith('/'):
                    liq = os.getcwd() + '/' + liq
                if os.path.exists(liq):
                    self.create_liquidsoap_systemd_unit(liq)
                    break
                else:
                    click.secho("{} not found".format(liq), fg='red')
            else:
                self.liquid_service_name = None
                break

    def create_liquidsoap_systemd_unit(self, liq_path):
        os.makedirs(self.path_systemd_units, exist_ok=True)
        self.liquid_service_name = self.basename + '_soap'
        liquid_binary = shutil.which('liquidsoap')
        if not liquid_binary:
            raise click.ClickException("Can't find complete path to `liquidsoap` executable.")

        pid_path = os.getcwd() + '/' + self.liquid_service_name + '.pid'
        log_path = os.getcwd() + '/' + self.liquid_service_name + '.log'

        run_script = os.getcwd() + '/' + self.liquid_service_name + '.liq'
        with open(run_script, 'w') as service:
            click.echo("Creating Liquidsoap wrapper script: "+run_script)
            service.write(LIQUID_TEMPLATE.format(
                liquidsoap_binary=liquid_binary,
                log_path=log_path,
                pid_path=pid_path,
                liq_path=liq_path,
            ))

        liquid_service_file = self.path_systemd_units + self.liquid_service_name + '.service'

        with open(liquid_service_file, 'w') as service:
            click.echo("Creating systemd unit for Liquidsoap: "+liquid_service_file)
            service.write(LIQUID_UNIT_TEMPLATE.format(
                basename=self.basename,
                pid_path=pid_path,
                base_dir=os.getcwd(),
                liquidsoap_binary=liquid_binary,
                run_script=run_script,
            ))

    def create_systemd_unit(self):
        os.makedirs(self.path_systemd_units, exist_ok=True)
        if self.liquid_service_name:
            self.service_name = self.basename + '_gel'
        else:
            self.service_name = self.basename

        service_file = self.path_systemd_units + self.service_name + '.service'

        with open(service_file, 'w') as service:
            click.echo("Creating systemd unit for Showergel: "+service_file)
            service.write(SHOWERGEL_UNIT_TEMPLATE.format(
                basename=self.basename,
                base_dir=os.getcwd(),
                toml_path=self.path_toml,
                showergel=shutil.which('showergel'),
            ))

        os.system("systemctl --user daemon-reload")

    def enable_systemd_unit(self):
        if self.service_name:
            os.system("systemctl --user enable "+self.service_name)
        if self.liquid_service_name:
            os.system("systemctl --user enable "+self.liquid_service_name)
        if self.service_name or self.liquid_service_name:
            click.echo("Enabling lingering (to start services at boot)")
            os.system("loginctl enable-linger")
        self.enabled = True

    def recap(self):
        click.secho("\nAll done ! Keep information below for future reference:",
            fg='green', bold=True)
        click.echo("Current folder will contain Showergel and Liquidsoap's log files, with a '.log' extension.")

        if self.liquid_service_name:
            click.secho("\nThe companion Liquidsoap script has been installed as a system service", bold=True)
            if self.enabled:
                click.echo("It will start automatically when rebooting.")
            click.echo("You can use the following commands:")
            click.echo(" * systemctl --user start "+self.liquid_service_name)
            click.echo(" * systemctl --user stop "+self.liquid_service_name)
            click.echo(" * systemctl --user restart "+self.liquid_service_name)
            click.echo(" * systemctl --user status "+self.liquid_service_name)
            click.echo(" * systemctl --user disable "+self.liquid_service_name)
            click.echo(" * systemctl --user enable "+self.liquid_service_name)

        if self.service_name:
            click.secho("\nShowergel has been installed as a system service", bold=True)
            if self.enabled:
                click.echo("It will start automatically when rebooting.")
            click.echo("You can use the following commands:")
            click.echo(" * systemctl --user start "+self.service_name)
            click.echo(" * systemctl --user stop "+self.service_name)
            click.echo(" * systemctl --user restart "+self.service_name)
            click.echo(" * systemctl --user status "+self.service_name)
            click.echo(" * systemctl --user disable "+self.service_name)
            click.echo(" * systemctl --user enable "+self.service_name)
            click.echo("\nOnce started, you can access Showergel's interface at http://localhost:{}/".format(self.port))
        else:
            click.echo("You can start showergel by invoking:")
            click.echo("showergel serve "+self.path_toml)

        click.echo("\nBe careful to restart Showergel after editing the .toml file")

        click.secho("\nWe advise you backup regularly the following files by copying them to an external support:",
            bold=True)
        click.echo(" * "+self.path_db)
        click.echo(" * "+self.path_toml)
        click.echo("")
        click.secho("\nWe advise you to read and tune Showergel's configuration: "+self.path_toml,
            bold=True)
        click.echo("")


@showergel_cli.command()
@click.option('--no-revert-on-failure', is_flag=True, help="If you want to develop/debug this installer")
def install(no_revert_on_failure):
    """
    Set-up a new Showergel/Liquidsoap installation
    """
    installer = Installer()
    try:
        installer.hello()
        installer.ask_basename()
        installer.ask_port()
        installer.check_no_overwriting()

        if click.confirm("\nShould we install {} as a system service ?"
            .format(installer.basename), default=True):
            installer.ask_liquid_script()
            installer.create_systemd_unit()

        # do this now because adding Liquidsoap script as a service changes the log path
        installer.create_toml_and_db()
        if installer.service_name and click.confirm("\nStart the service(s) at boot ?"
            , default=True):
            installer.enable_systemd_unit()
    except Exception:
        if not no_revert_on_failure:
            installer.revert()
        raise

    installer.recap()


@showergel_cli.command()
@click.argument('config_path')
def update(config_path):
    """
    Update/restore a Showergel installation
    """
    installer = Installer()
    installer.create_db_schema(path_toml=config_path)
    click.secho("DB is up-to-date", fg='green', bold=True)
    # TODO support restore: re-create/re-enable systemd units


@showergel_cli.command()
def develop():
    """
    Set-up a new Showergel installation, for development or debugging
    """
    installer = Installer()
    installer.check_no_overwriting()
    installer.create_toml_and_db(dev=True)
    installer.recap()
