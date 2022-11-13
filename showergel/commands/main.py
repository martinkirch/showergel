import click

@click.group()
def showergel_cli():
   pass

# load sub-commands
from . import install, serve, version

if __name__ == '__main__':
    showergel_cli()
