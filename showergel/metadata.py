"""
============
Metadata log
============

This module contains functions that process and store the metadata of tracks
played by Liquidsoap.
"""

import logging
import re
from typing import Type, Dict, List, Tuple
from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.exc import IntegrityError

from showergel.db import Base


_log = logging.getLogger(__name__)

LIQUIDSOAP_DATEFORMAT = r"%Y/%m/%d %H:%M:%S"

def to_datetime(date_string):
    """
    Parameters:
        date_string(str): a string representation, using either Liquidsoap's on_air
            format (``YYYY/MM/DD HH:MM:SS``) or ISO 8601.
    Return:
        (datetime): parsed datetime
    """
    try:
        return datetime.strptime(date_string, LIQUIDSOAP_DATEFORMAT)
    except ValueError:
        pass
    return datetime.fromisoformat(date_string)


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    on_air = Column(DATETIME, nullable=False, unique=True, index=True)
    artist = Column(String)
    title = Column(String)
    album = Column(String)
    source = Column(String)
    initial_uri = Column(String)

    extra = relationship("LogExtra", back_populates="log", lazy='joined')

    @staticmethod
    def save_metadata(config, db, data:Dict):
        """
        Save the metadata provided by Liquidsoap.

        We enforce uniqueness of the ``on_air`` field ; repeated posts with the
        same date-time will be ignored.

        Fields that do not fit into our ``log`` table are saved to ``log_extra``
        if they match one in the ``extra_fields`` configuration.
        Empty values are not saved.
        When ``initial_uri`` is not provided by Liquidsoap, we might use
        ``source_url`` instead (this may happen for example from ``http.input``).
        """
        try:
            log_entry = Log(on_air=to_datetime(data['on_air']))
        except KeyError:
            _log.warning("Missing on_air in %r", data)
            raise ValueError("Metadata should at least contain on_air") from None

        if not data.get('initial_uri') and data.get('source_url'):
            log_entry.initial_uri = data['source_url']
            del data['source_url']

        for column in ['artist', 'title', 'album', 'source', 'initial_uri']:
            if data.get(column):
                setattr(log_entry, column, data[column])

        try:
            db.add(log_entry)
            db.flush()
        except IntegrityError:
            _log.debug("We already have metadata at given on_air - ignoring %r", data)
            db.rollback()
            return

        for couple in FieldFilter.filter(data, config=config):
            db.add(LogExtra(log=log_entry, key=couple[0], value=couple[1]))

    @classmethod
    def get(cls, db:Type[Session], start:String=None, end:String=None,
        limit:int=10, chronological:bool=None) -> List:

        query = db.query(cls)

        if start:
            query = query.filter(cls.on_air >= to_datetime(start))
        if end:
            query = query.filter(cls.on_air <= to_datetime(end))

        if chronological:
            query = query.order_by(cls.on_air.asc())
        else:
            query = query.order_by(cls.on_air.desc())

        if not(start and end):
            if not limit:
                limit = 10
            query = query.limit(limit)

        return [l.to_dict() for l in query]

    def to_dict(self):
        d = {'on_air': self.on_air.isoformat()}
        if self.artist:
            d['artist'] = self.artist
        if self.title:
            d['title'] = self.title
        if self.album:
            d['album'] = self.album
        if self.source:
            d['source'] = self.source
        if self.initial_uri:
            d['initial_uri'] = self.initial_uri

        for additional in self.extra:
            d[additional.key] = additional.value

        return d


class LogExtra(Base):
    __tablename__ = 'log_extra'

    id = Column(Integer, primary_key=True)
    log_id = Column(Integer, ForeignKey(
        'log.id', onupdate='CASCADE', ondelete='CASCADE', deferrable=True, initially='DEFERRED'
    ))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    log = relationship("Log", back_populates="extra")



class FieldFilter(object):
    # this is a lazy implementation of a singleton ; in the same program it
    # will always be called with the same config object, so we don't need much
    # thread-safety

    _fields:set = None
    _wildcards:list = None

    @classmethod
    def setup(cls, config):
        try:
            extra_fields = config['metadata_log.extra_fields']
        except KeyError: # if `[metadata_log] extra_fields`  is not in the config
            extra_fields = []
        fields = set()
        wildcards = list()
        for entry in extra_fields:
            if '*' in entry:
                wildcards.append(re.compile(entry.strip().replace('*', '.*')))
            else:
                fields.add(entry.strip())
        cls._fields = fields
        cls._wildcards = wildcards
        _log.debug("Will keep metadata fields %r", fields)
        _log.debug("Will keep medadata fields matching %r", wildcards)

    @classmethod
    def filter(cls, data:Dict, config:dict=None, only_extra=True) -> List[Tuple[str, str]]:
        """
        Extracts metadata entries that fit in our ``log_extra`` table.
        Expects you called ``setup()`` before, or provide ``config``.

        Parameter:
            data: as provided by Liquidsoap
            config: daemon configuration ; we search for ``extra_fields`` in the ``metadata_log`` section.
            only_extra: tells if it should filter out fields that fit in the ``log`` table.
        Returns:
            A list of ``(key, value)`` couples, for each key in the input
            dictionary that matches ``extra_fields``.
        """
        if cls._fields is None:
            if config is None:
                raise ValueError("FieldFilter is not configured yet ! Caller should provide config, or call .setup(config) before.")
            else:
                cls.setup(config)
        result = list()
        for k, v in data.items():
            if k and v and (
                ((not only_extra) and k in [
                'on_air', 'artist', 'title', 'album', 'source', 'initial_uri'])
                or
                (k in cls._fields)
                or
                (any(rule.match(k) for rule in cls._wildcards))
            ):
                result.append((k, v))
        return result
