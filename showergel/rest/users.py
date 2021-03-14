"""
Users RESTful interface
=======================
"""
import logging

from bottle import request, HTTPError, HTTP_CODES

from showergel.users import User
from .. import app

_log = logging.getLogger(__name__)

@app.post("/login")
def post_login(db):
    """
    Should be called by Liquidsoap to authenticate harbor users.
    It returns the matched user information as a JSONobject, or a 404 error.
    Call it from Liquidsoap as follows:
    
    .. code-block:: ocaml

        ## TODO how is it logged to metadata ?

        def auth_function(user, password) =
            reponse = string_of(http.post(
                headers=[("Content-Type", "application/json")],
                "http://localhost:2345/login",
                data=json_of([
                    ("username", user), ("password", password)
                ])
            ))
            if string.contains(
                prefix="((\"HTTP/1.0\", 200, \"OK\"),",
                reponse) then
                log("Access granted to #{user}")
                true
            else
                log("Access denied to #{user}")
                false
            end
        end

        harbor = input.harbor(auth=auth_function, ...
    """
    try:
        username = request.json.get('username')
        password = request.json.get('password')
    except Exception:
        raise HTTPError(status=404, body=HTTP_CODES[404]) from None
    user = User.check(db, username, password)
    if user:
        return user.to_dict()
    raise HTTPError(status=404, body=HTTP_CODES[404])

@app.get("/users")
def get_users(db):
    """
    :>jsonarr username:
    :>jsonarr created_at:
    :>jsonarr modified_at:
    """
    return {"users": User.list(db)}


@app.put("/users")
def put_users(db):
    """
    Create an user

    :<json username:
    :<json password:
    :>json username:
    :>json created_at:
    :>json modified_at:
    """
    if request.json.get('password') and request.json.get('username'):
        username = request.json.get('username')
        existing = User.from_username(db, username)
        if existing:
            raise HTTPError(status=409, body=f"{username} is already registered")
        else:
            user = User.create(db, username, request.json.get('password'))
            if user:
                return user.to_dict()
    raise HTTPError(status=400, body="Non-empty 'username' and 'password' are expected.")


@app.delete("/users")
def delete_users(db):
    """
    Delete someone's user account

    :query username:
    """
    User.delete(db, username=request.params.username)
    return {}
