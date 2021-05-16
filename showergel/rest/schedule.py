"""
Schedule RESTful interface
==========================
"""
import logging

from bottle import request, HTTPError
import arrow

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
    :<json when: Event time (ISO 8601 with time zone info)
    :>json event_id: created event's ID
    """
    scheduler = Scheduler.get()
    try:
        return {
            'event_id': scheduler.command(
                request.json.get('command'),
                request.json.get('when'),
            )
        }
    except (ValueError, TypeError, AttributeError) as error:
        _log.exception(error)
        raise HTTPError(status=400, body=str(error))
    except KeyError as error:
        _log.exception(error)
        raise HTTPError(status=409, body=str(error))


@schedule_app.get("/schedule")
def get_schedule(db):
    """
    List upcoming events. For each event, expect:
     * ``event_id``
     * ``when`` (ISO 8601)
     * ``command``

    :>json schedule: list of scheduled events
    """
    scheduler = Scheduler.get()
    return {
        'schedule': scheduler.upcoming(),
    }

@schedule_app.delete("/schedule/<event_id>")
def delete_schedule(db, event_id):
    scheduler = Scheduler.get()
    try:
        scheduler.delete(event_id)
    except KeyError as error:
        raise HTTPError(status=404, body=str(error))
