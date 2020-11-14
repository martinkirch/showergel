"""
Showergel interactive installer

see the ``install`` section of the README file.
"""

import logging
import os
import os.path
import shutil

import click

from . import get_config
from .db import SessionContext, Base
from . import metadata # must be there for schema discovery

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
address = localhost
port = {port:d}


############# Logging configuration ##########

[loggers]
keys = root

[handlers]
keys = main

[formatters]
keys = generic

[logger_root]
level = DEBUG
handlers = main

[handler_main]
formatter = generic
level = NOTSET
{handler}

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(threadName)s][%(name)s:%(lineno)s] %(message)s

"""

# borrowed from liquidsoap.systemd.in in savonet's liquidsoap-daemon
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
WantedBy=multi-user.target
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
ExecStart=showergel {ini_path}

[Install]
WantedBy=multi-user.target
"""


class Installer(object):
    def __init__(self):
        self.basename = 'showergel'
        self.port = '1234'
        click.secho("Welcome to showergel installer !",
            fg='green', bold=True)
        click.echo("\nWe will ask for a few parameters.\n\nWhen in doubt, just press Enter and we'll use the default value (shown between square brackets).\nHit Ctlr+C to abort.")
        self.liquid_service_name = None
        self.service_name = None

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
        return os.getcwd() + '/' + self.basename + '.log'

    def _potential_paths(self):
        for path in [
            self.path_ini,
            self.path_db,
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

    def ask_basename(self):
        click.echo("\nHow should we call the installation ?\nWe need a simple name (use only letters and numbers) for the future files and service.")
        while True:
            basename = click.prompt("Installation basename", default=self.basename)
            if basename.isalnum():
                self.basename = basename
                break
            else:
                click.secho("Use only letters and numbers", color='red')

    def ask_port(self):
        click.echo("\nWhich port should we use for Showergel's interface ? Just ensure nothing else is already using it.")
        port = click.prompt("Showergel port", default=self.port, type=int)
        self.port = port

    def check_no_overwriting(self):
        for path in self._potential_paths():
            if os.path.exists(path):
                raise click.ClickException(f"{path} already exists, which suggests that Showergel is already installed. Or maybe install with another basename.")

    def create_ini(self, dev=False):
        if dev:
            handler = "class = logging.handlers.StreamHandler\nargs = (sys.stderr,)"
        else:
            handler = "class = logging.handlers.RotatingFileHandler\nargs=('{}', 'a', 1000000, 10)".format(
                self.path_log)
        with open(self.path_ini, 'w') as ini:
            ini.write(INI_TEMPLATE.format(
                db=self.path_db,
                port=self.port,
                handler=handler
            ))

    def create_db(self):
        config = get_config(path=self.path_ini)
        SessionContext(config=config)
        Base.metadata.create_all(SessionContext.engine)

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
            service.write(LIQUID_TEMPLATE.format(
                liquidsoap_binary=liquid_binary,
                log_path=log_path,
                pid_path=pid_path,
                liq_path=liq_path,
            ))

        liquid_service_file = self.path_systemd_units + self.liquid_service_name + '.service'

        with open(liquid_service_file, 'w') as service:
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
            service.write(SHOWERGEL_UNIT_TEMPLATE.format(
                basename=self.basename,
                base_dir=os.getcwd(),
                ini_path=self.path_ini,
            ))

        os.system("systemctl --user daemon-reload")

    def enable_systemd_unit(self):
        if self.service_name:
            os.system("systemctl --user enable "+self.service_name)
        if self.liquid_service_name:
            os.system("systemctl --user enable "+self.liquid_service_name)
        if self.service_name or self.liquid_service_name:
            os.system("loginctl enable-linger")

    def recap(self):
        click.secho("All done ! Keep all information above for future reference:",
            fg='green', bold=True)
        click.secho("\nWe advise you backup regularly the following files by copying them to an external support:",
            bold=True)
        click.echo(" * "+self.path_db)
        click.echo(" * "+self.path_ini)

@click.command()
@click.option('--dev', is_flag=True)
@click.option('--no-revert-on-failure', is_flag=True)
def main(dev, no_revert_on_failure):
    installer = Installer()
    if (dev):
        installer.check_no_overwriting()
        installer.create_ini(dev=True)
        installer.create_db()
    else:
        try:
            installer.ask_basename()
            installer.ask_port()
            installer.check_no_overwriting()
            installer.create_ini()
            installer.create_db()

            if click.confirm("\nShould we install {} as a system service ?"
                .format(installer.basename), default=True):
                installer.ask_liquid_script()
                installer.create_systemd_unit()
                if click.confirm("\nStart the service(s) now and enable it at boot ?"
                    , default=True):
                    installer.enable_systemd_unit()
        except Exception:
            if not no_revert_on_failure:
                installer.revert()
            raise

    installer.recap()
