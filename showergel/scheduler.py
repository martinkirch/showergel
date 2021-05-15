"""
===============================
Showergel's APScheduler wrapper
===============================

All accesses to APScheduler are wrapped here: scheduler creation, but also
job storage and definition.
"""
import logging
from typing import Type

from sqlalchemy.engine import Engine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import EVENT_JOB_ERROR

from showergel.liquidsoap_connector import TelnetConnector

_log = logging.getLogger(__name__)


class Scheduler:
    """
    Only one instance of this class should exist in the Showergel process:
    call :ref:`setup` once, then access the instance with :ref:`get`.
    """

    __instance = None

    @classmethod
    def setup(cls, db_engine:Type[Engine], liquidsoap_connection:Type[TelnetConnector]):
        cls.__instance = cls(db_engine, liquidsoap_connection)

    @classmethod
    def get(cls):
        if not cls.__instance:
            raise ValueError("Scheduler.setup() has not been called yet")
        return cls.__instance

    def __init__(self, db_engine:Type[Engine], liquidsoap_connection:Type[TelnetConnector]):
        self.liquidsoap = liquidsoap_connection
        jobstores = {
            'default': SQLAlchemyJobStore(engine=db_engine)
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.add_listener(self._on_job_error, EVENT_JOB_ERROR)
        self.scheduler.start()

    def _on_job_error(self, event):
        _log.critical("Error caught on job#%s scheduled at %s:",
            event.job_id, event.scheduled_run_time)
        if event.exception:
            _log.exception(event.exception)
