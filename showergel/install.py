import logging

from . import get_config
from .db import SessionContext, Base
from . import metadata # must be there for schema discovery

_log = logging.getLogger(__name__)

def main():
    config = get_config()
    _log.info("Checking DB schema...")
    SessionContext(config=config)
    Base.metadata.create_all(SessionContext.engine)
    _log.info("Done")
