"""
Schedule RESTful interface
==========================
"""
import logging
from datetime import datetime

from bottle import request, HTTPError

from showergel.showergel_bottle import ShowergelBottle
from showergel.scheduler import Scheduler

_log = logging.getLogger(__name__)

schedule_app = ShowergelBottle()

@schedule_app.put("/schedule")
def put_schedule(db):
    """
    Schedule event creation. Note that at most one event can be registered at a
    given date.

    :<json command: Liquidsoap command
    :<json when: Event time (ISO 8601)
    :>json event_id: created event's ID
    """
    scheduler = Scheduler.get()
    try:
        return {
            'event_id': scheduler.command(
                request.json.get('command'),
                datetime.fromisoformat(request.json.get('when')),
            )
        }
    except (ValueError, TypeError, AttributeError) as error:
        _log.debug(error)
        raise HTTPError(status=400, body=str(error))
    except KeyError as error:
        _log.debug(error)
        raise HTTPError(status=409, body=str(error))
    