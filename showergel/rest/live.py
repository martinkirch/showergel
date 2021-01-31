"""
====================================
RESTful interface to current playout
====================================
"""
from datetime import datetime

from bottle import request

from .. import app


@app.get("/live")
def get_live():
    """
    GET ``/live``

    Currently only returns server time.
    """
    return {
        "server_time": datetime.now().isoformat()
    }
