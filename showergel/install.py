"""
Showergel interactive installer

see the ``install`` section of the README file.
"""

import logging
import os
import os.path
import shutil
import socket
from configparser import ConfigParser

import click
from sqlalchemy import engine_from_config



_log = logging.getLogger(__name__)

INI_TEMPLATE = """
[db]
sqlalchemy.url = sqlite:///{db}

############### Metadata logger ###############
[metadata_log]

# list of metadata fields that should *not* be stored
# you can use * to represent any characters or nothing
# for example, "musicbraiz*" will ignore "musicbrainz"
# but also "musicbrainz_artist_id" or "musicbrainz album type"
ignore_fields = musicbrainz*, comment*, itunes*, lyrics



############## Server configuration ##########
[listen]
# Showergel's interface will be available at http://[address]:[port]/
# As there is no security check, be careful to keep the address on a private network.
address = localhost
port = {port:d}
{debug}

############# Logging configuration ##########

[loggers]
keys = root

[handlers]
keys = main

[formatters]
keys = generic

[logger_root]
level = {log_level}
handlers = main

[handler_main]
formatter = generic
level = NOTSET
{handler}

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(threadName)s][%(name)s:%(lineno)s] %(message)s

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

set("log.file",true)
set("log.file.path","{log_path}")
set("init.daemon",true)
set("init.daemon.pidfile",true)
set("init.daemon.pidfile.path","{pid_path}")
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
ExecStart={showergel} {ini_path}

[Install]
WantedBy=default.target
"""


class Installer(object):
    def __init__(self):
        self.basename = 'showergel'
        self.port = 2345
        self.liquid_service_name = None
        self.service_name = None
        self.enabled = False

        home = os.environ.get('HOME')
        if not home:
            raise click.ClickException("Cannot find HOME environment variable")
        self.path_systemd_units = home + "/.config/systemd/user/"

    @property
    def path_ini(self):
        return os.getcwd() + '/' + self.basename + '.ini'

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
            self.path_ini,
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

    def create_ini_and_db(self, dev=False):
        if dev:
            handler = "class = logging.StreamHandler\nargs = (sys.stderr,)"
            debug = "debug = True"
            log_level = "DEBUG"
        else:
            handler = "class = logging.handlers.RotatingFileHandler\nargs=('{}', 'a', 1000000, 10)".format(
                self.path_log)
            debug = ""
            log_level = "INFO"
        with open(self.path_ini, 'w') as ini:
            click.echo("Writing configuration file: "+self.path_ini)
            ini.write(INI_TEMPLATE.format(
                db=self.path_db,
                port=self.port,
                handler=handler,
                debug=debug,
                log_level=log_level,
            ))
        click.echo("Initializing database: "+self.path_db)
        self.create_db_schema()

    def create_db_schema(self, path_ini=None):
        if not path_ini:
            path_ini = self.path_ini

        from showergel import Base
        # indirectly import all Base subclasses:
        from showergel import rest

        config = ConfigParser()
        config.read(path_ini)
        engine = engine_from_config(config['db'])
        Base.metadata.create_all(engine)

    def ask_liquid_script(self):
        click.echo("\nIf you would like to also create a systemd service for your Liquidsoap script, enter its path below. Otherwise, leave blank.")
        while True:
            liq = click.prompt("Path to Liquidsoap script (absolute or relative)")
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
                ini_path=self.path_ini,
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
            click.echo("showergel "+self.path_ini)

        click.echo("\nBe careful to restart Showergel after editing the .ini file")

        click.secho("\nWe advise you backup regularly the following files by copying them to an external support:",
            bold=True)
        click.echo(" * "+self.path_db)
        click.echo(" * "+self.path_ini)
        click.echo("")

@click.command()
# TODO : currently --help shows "--update TEXT" - how to change TEXT ?
@click.option('--update', help="Check/update the DB schema after a software update")
@click.option('--dev', is_flag=True, help="If you want to develop/debug Showergel")
@click.option('--no-revert-on-failure', is_flag=True, help="If you want to develop/debug this installer")
def main(update, dev, no_revert_on_failure):
    installer = Installer()
    if (update):
        installer.create_db_schema(path_ini=update)
        click.secho("DB is up-to-date", fg='green', bold=True)
    elif (dev):
        installer.check_no_overwriting()
        installer.create_ini_and_db(dev=True)
        installer.recap()
    else:
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
            installer.create_ini_and_db()
            if installer.service_name and click.confirm("\nStart the service(s) at boot ?"
                , default=True):
                installer.enable_systemd_unit()
        except Exception:
            if not no_revert_on_failure:
                installer.revert()
            raise

        installer.recap()
