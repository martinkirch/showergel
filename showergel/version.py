import logging
from importlib.metadata import version

_log = logging.getLogger(__name__)

def get_version() -> str:
    """
    Get Showergel package's version version
    """
    try:
        return version("showergel")
    except Exception as excn:
        _log.warning(excn)
    return "demo"
