"""
Schedule RESTful interface
==========================
"""
import logging

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


@schedule_app.put("/schedule/cartfolder")
def put_schedule_cartfolder(db):
    """
    Cartfolders can be scheduled to play weekly ; this action will schedule
    a cartfolder to play at a given time on one or a few weekdays.

    :<json name: Cartfolder name
    :<json day_of_week: Weekday(s), starting from 0 for Monday - if given a few, write them as 0,2,6
    :<json hour: Hour of day (0-23)
    :<json minute:
    :<json timezone: for example "Europe/Paris"
    :>json event_id: created event's ID
    """
    scheduler = Scheduler.get()
    try:
        p = request.json
        return {
            'event_id': scheduler.cartfolder(
                p['name'],
                p['day_of_week'],
                int(p['hour']),
                int(p['minute']),
                p['timezone']
            )
        }
    except (ValueError, TypeError, KeyError) as error:
        _log.exception(error)
        raise HTTPError(status=400, body=str(error))
    except IndexError as error:
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
