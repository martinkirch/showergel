"""
=============================
Showergel's RESTful interface
=============================

This module interfaces Showergel with the outside world, with a REST interface
implemented with the Bottle framework.

Launch by invoking::

    showergel config.ini

Responses are in JSON, ``PUT`` and ``POST`` requests should attach their data as JSON,
``GET`` and ``DELETE`` should bundle parameters in a query string (``application/x-www-form-urlencoded``).


"""

from . import metadata_log
from . import users

