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

    def _handle(self, environ):
        """
        Workaround for https://github.com/bottlepy/bottle/issues/602
        """
        environ["PATH_INFO"] = environ["PATH_INFO"].encode("utf8").decode("latin1")
        return super()._handle(environ)
