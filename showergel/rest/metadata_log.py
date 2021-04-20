"""
Metadata log RESTful interface
==============================
"""

from bottle import request, HTTPError

from showergel.showergel_bottle import ShowergelBottle
from showergel.metadata import Log

metadata_log_app = ShowergelBottle()

@metadata_log_app.get("/metadata_log")
def get_metadata_log(db):
    """
    Without parameters, ``GET /metadata_log`` returns the 10 most recent metadata items played.
    The following query parameters can be provided

    :query string start: (ISO 8601 format) define an inclusive query interval
    :query string end: define an inclusive query interval
    :query int limit: restricts the number of results (and defaults to 10).
        It is ignored if ``start`` and ``end`` are provided.
    :query bool chronological: may be set to anything non-empty (use ``1`` or ``true``),
        otherwise results are sorted recent first.
        Doesn't affect the interpretation of ``start`` and ``end``.
    
    :>json metadata_log: logged metadata matching the query parameters.
    """
    return {
        'metadata_log': Log.get(db,
            start=request.params.start,
            end=request.params.end,
            limit=request.params.limit,
            chronological=bool(request.params.chronological),
        )
    }

@metadata_log_app.post("/metadata_log")
def post_metadata_log(db):
    """
    Should be called by Liquidsoap to save tracks' metadata.
    See :ref:`liq_metadata`.
    """
    try:
        if not request.json:
            raise ValueError("No JSON data POSTed - maybe headers are missing")
        Log.save_metadata(metadata_log_app.config, db, request.json)
    except ValueError as value_error:
        raise HTTPError(status=400, body=str(value_error))
    return {}
