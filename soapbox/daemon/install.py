from .metadata import install_metadata_db
from . import get_config

def main():
    conf = get_config()
    install_metadata_db(conf)
