"""
=============================
Showergel's RESTful interface
=============================

This module interfaces Showergel with the outside world, with a REST interface
implemented with the Bottle framework.

Launch by invoking::

    showergel config.toml

Responses are in JSON, ``PUT`` and ``POST`` requests should attach their data as JSON,
``GET`` and ``DELETE`` should bundle parameters in a query string (``application/x-www-form-urlencoded``).


"""

from .metadata_log import metadata_log_app
from .users import users_app
from .live import live_app
from .schedule import schedule_app

sub_apps = [metadata_log_app, users_app, live_app, schedule_app]
