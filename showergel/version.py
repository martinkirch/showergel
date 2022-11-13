import logging
import pkg_resources

_log = logging.getLogger(__name__)

def get_version() -> str:
    """
    Get Showergel package's version version
    """
    try:
        return pkg_resources.get_distribution("showergel").version
    except Exception as excn:
        _log.warning(excn)
    return "demo"
