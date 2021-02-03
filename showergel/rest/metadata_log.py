"""
==============================
Metadata log RESTful interface
==============================
"""

from bottle import request, HTTPError

from showergel.metadata import Log
from .. import app


@app.get("/metadata_log")
def get_metadata_log(db):
    """
    GET ``/metadata_log``
    -----------------

    Return an array of logged metadata.
    Possible parameters:

    * ``chronological`` may be set to anything non-empty (use ``1`` or ``true``),
        otherwise results are sorted recent first.
        Doesn't affect the interpretation of ``start`` and ``end``.
    * log interval, as ``start`` and ``end`` (inclusive).
        For example ``start=2020-12-01 12:00:00&end=2020-12-01 14:00:00``.
    * if ``start`` or ``end`` is missing, ``limit`` restricts the number of results (and defaults to 10).

    Therefore, ``GET /metadata_log`` returns the 10 most recent metadata items played.
    """
    return {
        'metadata_log': Log.get(db,
            start=request.params.start,
            end=request.params.end,
            limit=request.params.limit,
            chronological=bool(request.params.chronological),
        )
    }

@app.post("/metadata_log")
def post_metadata_log(db):
    """
    POST ``/metadata_log``
    -----------------

    Save Liquidsoap's metadata, it can be called from Liquidsoap by::

        def post_to_daemon(m)
            response = http.post("http://localhost:4321/metadata_log", data=json_of(m))
            log(label="http_posted", string_of(response))
        end

        radio = on_metadata(post_to_daemon, source)

    **Note** that although Showergel avoids inserting duplicated metadata,
    Liquidsoap may repeat one source's metadata later on if one operator
    uses the default ``replay_metadata=true``. This is likely to happen if
    you're using a track-insensitive ``fallback`` that skips previous source's
    track before switching.
    In other words, if you get duplicates in the metadata log,
    you might avoid them by adding ``replay_metadata=false`` to your track-insensitive
    ``fallback``/``random``/``rotate``/``switch`` operators.
    """
    try:
        if not request.json:
            raise ValueError()
        Log.save_metadata(app.config, db, request.json)
    except ValueError as value_error:
        raise HTTPError(status=400, body=str(value_error))
    return {}
