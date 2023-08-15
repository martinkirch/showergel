"""
===============================
Showergel's APScheduler wrapper
===============================

All accesses to APScheduler are wrapped here: scheduler creation, but also
job storage and definition.
"""
from __future__ import annotations
from typing import List, Dict
import logging

from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.job import Job
import arrow

from showergel.liquidsoap_connector import Connection
from showergel.metadata import Log
from showergel.cartfolders import CartFolders, EmptyCartException

_log = logging.getLogger(__name__)


# Scheduled "jobs" should be independant functions because APS must be able to
# serialize all their parameters (that wouldn't work with self:Scheduler)

def _do_command(command):
    """
    One-time scheduled Liquidsoap command
    """
    connection = Connection.get()
    _log.info("Running scheduled command: %s", command)
    result = connection.command(command)
    _log.info("Liquidsoap replied: %s", result)
    Scheduler.dbsession.add(Log(
        on_air=arrow.get(tzinfo='local').to('utc').datetime,
        source="showergel_scheduler",
        initial_uri=command,
    ))
    Scheduler.dbsession.commit()

def _do_enqueue_cart(cartname):
    """
    Function called each time a cart is scheduled. Pushes the next file to queue.
    """
    if not CartFolders.liquidsoap_queue:
        return
    try:
        nextpath = CartFolders.get()[cartname].next()
    except KeyError:
        _log.critical("A cart called %s has been scheduled now, but does not appear in Showergel's configuration. Please clean the schedule.", cartname)
        return
    except EmptyCartException:
        _log.info("Cart %s should play now, but its folder is empty", cartname)
        return
    connection = Connection.get()
    command = f"{CartFolders.liquidsoap_queue}.push {nextpath}"
    _log.debug("Enqueuing cart folder: %s", command)
    result = connection.command(command)
    _log.debug("Liquidsoap replied: %s", result)


def serialize(job:Job) -> Dict:
    """
    Return:
        (dict): a dict describing an event and its next occurrence
    """
    if job.name == 'cartfolder':
        when = arrow.get(job.trigger.get_next_fire_time(None, arrow.utcnow().datetime)).isoformat()
    else: # job.name == 'command' or legacy jobs
        when = arrow.get(job.trigger.run_date).isoformat()
    return {
        'event_id': job.id,
        'type': job.name,
        'what': job.args[0],
        'when': when
    }

class Scheduler:
    """
    Only one instance of this class should exist in the Showergel process:
    call :ref:`setup` once, then access the instance with :ref:`get`.
    """

    __instance = None
    dbsession = None

    @classmethod
    def setup(cls, dbsession:Session, store_in_memory=False):
        """
        This should be called once, when starting the program.

        `store_in_memory` may be activated when you don't want to persist
        the schedule (this happens in demo mode or unit tests).
        """
        cls.__instance = cls(dbsession, store_in_memory)
        cls.dbsession = dbsession

    @classmethod
    def get(cls):
        """
        This is the only accessor of the programs's ``Scheduler`` instance.
        Return:
            (Scheduler):
        """
        if not cls.__instance:
            raise ValueError("Scheduler.setup() has not been called yet")
        return cls.__instance

    def __init__(self, dbsession:Session, store_in_memory):
        if store_in_memory:
            self.scheduler = BackgroundScheduler()
        else:
            jobstores = {
                'default': SQLAlchemyJobStore(engine=dbsession.get_bind())
            }
            self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self.scheduler.start()

    def _on_job_error(self, event):
        """
        Handles APScheduler's ``EVENT_JOB_ERROR`` by logging the job ID and
        the caught exception, if any.
        """
        _log.critical("Error caught on job#%s scheduled at %s:",
            event.job_id, event.scheduled_run_time)
        if event.exception:
            _log.exception(event.exception)

    def command(self, command:str, when:str) -> dict:
        """
        Squedule a Liquidsoap command. It will raise ``KeyError`` if a command
        was already scheduled at given date, or ``ValueError`` if given unusable
        parameters.
        Parameters:
            command (str): a complete Liquidsoap telnet command
            when (str): **UTC** time
        Return:
            (dict): serialized event info (see ``serialize``)
        """
        run_date = arrow.get(when).to('utc')
        if run_date < arrow.utcnow():
            raise ValueError("Please schedule something in the future, given date is in the past")
        if not command:
            raise ValueError("Please provide a non-empty command")
        try:
            job = self.scheduler.add_job(_do_command,
                id=str(run_date.float_timestamp),
                name='command',
                args=[command],
                trigger='date',
                run_date=run_date.datetime,
            )
        except ConflictingIdError:
            raise KeyError("A job is already scheduled at that time. Remove the existing one first")
        return serialize(job)

    def cartfolder(self, name:str, day_of_week:str, hour:int, minute:int, timezone:str) -> dict:
        """
        Schedule a cartfolder to play weekly at a given time.

        Raises ``KeyError`` if given cartfolder name does not exists,
        or ``IndexError`` if a cartfolder has the same schedule.
        Parameters:
            name (str): Cartfolder name
            day_of_week (str):  Weekday(s), starting from 0 for Monday - if given a few, write them as 0,2,6
            hour (int):
            minute (int):
            timezone (str): for example "Europe/Paris"
        Return:
            (dict): serialized event info (see ``serialize``)
        """
        _ = CartFolders.get()[name] # checks it exists
        try:
            h = str(hour).zfill(2)
            m = str(minute).zfill(2)
            job = self.scheduler.add_job(_do_enqueue_cart,
                id=f"{day_of_week}{h}{m}00{timezone}".replace('/', '_'), # thanks to the 00 we're ready for second precison
                name='cartfolder',
                args=[name],
                trigger='cron',
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
            )
        except ConflictingIdError:
            raise IndexError("A cartfolder already has the same schedule. Remove the existing one first")
        return serialize(job)


    def upcoming(self) -> List[Dict]:
        """
        Return:
            (list): upcoming events descriptions
        """
        events = {}
        for job in self.scheduler.get_jobs():
            as_dict = serialize(job)
            events[as_dict['when']] = as_dict
        return events

    def delete(self, event_id):
        """
        May raise KeyError if ``event_id`` does not exists
        """
        try:
            self.scheduler.remove_job(event_id)
        except JobLookupError:
            raise KeyError("Event not found")
