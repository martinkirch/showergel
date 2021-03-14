"""
RESTful interface to current playout
====================================
"""
from datetime import datetime

from .. import app


@app.get("/live")
def get_live():
    """
    Currently only returns server time.
    """
    return {
        "server_time": datetime.now().isoformat()
    }
