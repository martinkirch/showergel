import json
import logging

from bottle import Bottle, response

_log = logging.getLogger(__name__)

class ShowergelBottle(Bottle):

    catchall = True

    def default_error_handler(self, res):
        response.content_type = 'application/json'
        if (res.exception and
            isinstance(res.exception, json.JSONDecodeError) and
            "request.json" in res.traceback
            ):
            response.status = 400
            return json.dumps({"code": 400, "message": "Please send well-formed JSON"})
        else:
            if res.exception:
                _log.critical("Caught exception: %r", res.exception)
                _log.debug("Caught:", exc_info=res.exception)
            return json.dumps({"code": int(res.status_code), "message": res.body})
