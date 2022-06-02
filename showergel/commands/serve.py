import logging
from os import environ

import toml
import click
from .main import showergel_cli

from showergel import app

_log = logging.getLogger(__name__)

def read_bool_param(param):
    value = app.config.get('listen.'+param)
    if value in ('False', 'false'):
        return False
    else:
        return bool(value)

@showergel_cli.command()
@click.version_option()
@click.argument('config_path', type=click.Path(readable=True, allow_dash=False, exists=True))
@click.option('--verbose', is_flag=True, help="Sets logging level to DEBUG")
def serve(config_path, verbose):
    with open(config_path, 'r') as f:
        conf = toml.load(f)
    logging.config.dictConfig(conf['logging'])
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    app.config.load_dict(conf)

    try:
        port = int(app.config['listen.port'])
    except ValueError:
        port = int(environ[app.config['listen.port']])

    demo = read_bool_param('demo')
    debug = read_bool_param('debug')
    server = 'paste'
    if demo:
        # stubbing to :memory: works better with the default, mono-threaded server
        server = 'wsgiref'
    app.run(
        server=server,
        host=app.config['listen.address'],
        port=port,
        reloader=debug,
        quiet=not debug,
        demo=demo,
        debug=debug,
    )
