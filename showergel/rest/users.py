"""
Users RESTful interface
=======================
"""
import logging

from bottle import request, HTTPError, HTTP_CODES, response

from showergel.showergel_bottle import ShowergelBottle
from showergel.users import User

_log = logging.getLogger(__name__)

users_app = ShowergelBottle()

@users_app.post("/login")
def post_login(db):
    """
    Should be called by Liquidsoap to authenticate harbor users.
    It returns the matched user information as a JSONobject, or a 404 error.
    See :ref:`liq_login`.
    """
    try:
        username = request.json.get('user')
        password = request.json.get('password')
    except Exception:
        raise HTTPError(status=404, body=HTTP_CODES[404]) from None
    user = User.check(db, username, password)
    if user:
        return user.to_dict()
    raise HTTPError(status=404, body=HTTP_CODES[404])

@users_app.get("/users")
def get_users(db):
    """
    :>jsonarr username:
    :>jsonarr created_at:
    :>jsonarr modified_at:
    """
    return {"users": User.list(db)}


@users_app.put("/users")
def put_users(db):
    """
    User registration

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

@users_app.post("/users/<username>")
def update_user(db, username):
    """
    Update user attributes

    :<json password: optional
    :>json username:
    :>json created_at:
    :>json modified_at:
    """
    user = User.from_username(db, username)
    if user:
        new_password = request.json.get('password')
        if new_password:
            user.update_password(new_password)
        db.commit()
        return user.to_dict()
    else:
        raise HTTPError(status=404, body=HTTP_CODES[404])

@users_app.delete("/users/<username>")
def delete_users(db, username):
    """
    Delete someone's user account

    :>json deleted: username
    """
    User.delete(db, username=username)
    return {
        "deleted": username
    }
