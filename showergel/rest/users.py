"""
=======================
Users RESTful interface
=======================

"""


from bottle import request, HTTPError, HTTP_CODES

from showergel.users import User
from .. import app

@app.post("/login")
def post_login(db):
    """
    POST ``/login``
    ----------

    Username/password check. Returns the matched user object, or a 404 error.
    Call it from Liquidsoap as follows::

        TODO how to pass "/path/to/harbor_auth.py #{user} #{password}"
        TODO how is it logged to metadata ?

        def auth_function(user,password) = 
            response = http.post(
                "http://127.0.0.1:2345/login",
                data=json_of(metadata)
            )

            ret = get_process_output()
            if string.trim(ret) == "ok" then
                log("Access granted to #{user}")
                true
            else
                log("Access denied to #{user}")
                false
            end
        end

        harbor = input.harbor(auth=auth_function, ...
    """
    user = User.check(db, request.json.get('username'), request.json.get('password'))
    if user:
        return user.to_dict()
    else:
        raise HTTPError(status=404, body=HTTP_CODES[404])

@app.get("/users")
def get_users(db):
    """
    GET ``/users``
    ----------

    Return the list of harbor users
    """
    return User.list(db)


@app.put("/users")
def put_users(db):
    """
    PUT ``/users``
    ----------

    Create an user. Expects ``username`` and  ``password``. Returns the created user object.
    """
    user = User.create(db, request.json.get('username'), request.json.get('password'))
    if user:
        return user.to_dict()
    else:
        raise HTTPError(status=401, body=HTTP_CODES[401])


@app.delete("/users")
def delete_users(db):
    """
    DELETE ``/users?username=someone``
    ---------------------------

    Deletes ``someone``'s user account.
    """
    User.delete(db, request.query.username)
    return {}
