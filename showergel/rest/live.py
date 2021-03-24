"""
RESTful interface to current playout
====================================
"""
from datetime import datetime

from .. import app
from ..liquidsoap_connector import Connection


@app.get("/live")
def get_live():
    """
    The returned JSON object might contain many more fields, depending on what's
    in the current track's metadata. You can reasonably expect ``title`` and ``artist``.

    :>json source: name of the currently playing source
    :>json on_air: current track start time
    :>json status: status of the current source ("playing" or "connected to ...")
    :>json server_time: server's datetime
    """
    metadata = Connection.get().current()
    metadata["server_time"] = datetime.now().isoformat()
    return metadata
