"""
===============================
Showergel's APScheduler wrapper
===============================

All accesses to APScheduler are wrapped here: scheduler creation, but also
job storage and definition.
"""
import logging
from typing import Type, List, Dict

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from apscheduler.events import EVENT_JOB_ERROR
import arrow

from showergel.liquidsoap_connector import Connection
from showergel.metadata import Log

_log = logging.getLogger(__name__)


# Scheduled "jobs" should be independant functions because APS must be able to
# serialize all their parameters (that wouldn't work with self:Scheduler)
def _do_command(command):
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

class Scheduler:
    """
    Only one instance of this class should exist in the Showergel process:
    call :ref:`setup` once, then access the instance with :ref:`get`.
    """

    __instance = None
    dbsession = None

    @classmethod
    def setup(cls, db_engine:Type[Engine], store_in_memory=False):
        """
        This should be called once, when starting the program.

        `store_in_memory` may be activated when you don't want to persist
        the schedule (this happens in demo mode or unit tests).
        """
        cls.__instance = cls(db_engine, store_in_memory)
        factory = sessionmaker(bind=db_engine)
        cls.dbsession = factory()

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

    def __init__(self, db_engine:Type[Engine], store_in_memory):
        if store_in_memory:
            self.scheduler = BackgroundScheduler()
        else:
            jobstores = {
                'default': SQLAlchemyJobStore(engine=db_engine)
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

    def command(self, command:str, when:str) -> str:
        """
        Squedule a Liquidsoap command. It will raise ``KeyError`` if a command
        was already scheduled at given date, or ``ValueError`` if given unusable
        parameters.
        Parameters:
            command (str): a complete Liquidsoap telnet command
            when (str): **UTC** time
        Return:
            (str): job identifier
        """
        run_date = arrow.get(when).to('utc')
        if run_date < arrow.utcnow():
            raise ValueError("Please schedule something in the future, given date is in the past")
        if not command:
            raise ValueError("Please provide a non-empty command")
        try:
            job = self.scheduler.add_job(_do_command,
                id=str(run_date.float_timestamp),
                args=[command],
                trigger='date',
                run_date=run_date.datetime,
            )
        except ConflictingIdError:
            raise KeyError("A job is already scheduled at that time. Remove the existing one first")
        return job.id

    def upcoming(self) -> List[Dict]:
        """
        Return:
            (list): upcoming events descriptions
        """
        events = [
            {
                'event_id': job.id,
                'when': arrow.get(job.trigger.run_date).isoformat(),
                'command': job.args[0],
            } for job in self.scheduler.get_jobs()
        ]
        return events

    def delete(self, event_id):
        """
        May raise KeyError if ``event_id`` does not exists
        """
        try:
            self.scheduler.remove_job(event_id)
        except JobLookupError:
            raise KeyError("Event not found")
