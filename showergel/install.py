import logging

from .metadata import install_metadata_db
from . import get_config

_log = logging.getLogger(__name__)

def main():
    config = get_config()
    _log.info("Checking DB schema...")
    install_metadata_db(config)
    _log.info("Done")
