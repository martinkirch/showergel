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

import arrow
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.exc import IntegrityError

from showergel.db import Base
from showergel.liquidsoap_connector import Connection


_log = logging.getLogger(__name__)


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

        Repeated posts with the same artist and title will be ignored.

        Some fields are not posted as metadata by Liquidsoap (starting from v2),
        especially ``initial_uri``, ``source``, ``on_air``, and many possible
        things that the user might have set in ``extra_fields``.
        So we also query for more metadata via ``Connection``, and keep it only
        if artist and title match.

        Fields that do not fit into our ``log`` table are saved to ``log_extra``
        if they match one in the ``extra_fields`` configuration.
        Empty values are not saved.
        """
        connection = Connection.get()
        if connection:
            current = connection.current()
            if current and data.get('title') == current.get('title') and data.get('artist') == current.get('artist'):
                data.update(current)

        if 'on_air' in data:
            on_air = arrow.get(data['on_air'], tzinfo='local').to('utc').datetime
        else:
            on_air = arrow.get(tzinfo='local').to('utc').datetime
        log_entry = Log(on_air=on_air)

        if not data.get('initial_uri') and data.get('source_url'):
            log_entry.initial_uri = data['source_url']
            del data['source_url']

        for column in ['artist', 'title', 'album', 'source', 'initial_uri']:
            if data.get(column):
                setattr(log_entry, column, data[column])

        if 'artist' in data and 'title' in data:
            latest = Log.get(db, limit=1)
            if latest and latest[0]['artist'] == data['artist'] and latest[0]['title'] == data['title']:
                return

        db.add(log_entry)
        db.flush()

        for couple in FieldFilter.filter(data, config=config):
            db.add(LogExtra(log=log_entry, key=couple[0], value=couple[1]))

    @classmethod
    def get(cls, db:Type[Session], start:String=None, end:String=None,
        limit:int=10, chronological:bool=None) -> List:

        query = db.query(cls)

        if start:
            start_dt = arrow.get(start).to('utc').datetime
            query = query.filter(cls.on_air >= start_dt)
        if end:
            end_dt = arrow.get(end).to('utc').datetime
            query = query.filter(cls.on_air <= end_dt)

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
        d = {
            'on_air': arrow.get(self.on_air, tzinfo='utc').isoformat(),
            'artist': self.artist,
            'title': self.title,
            'album': self.album,
            'source': self.source,
            'initial_uri': self.initial_uri,
        }

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
