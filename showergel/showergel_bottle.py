import json

from bottle import Bottle, response

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
            return json.dumps({"code": int(res.status_code), "message": res.body})
