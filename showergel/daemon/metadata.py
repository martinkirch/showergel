"""
===============
Metadata logger
===============

This module contains functions that process and store the metadata of tracks
played by Liquidsoap.
"""

import logging
import sqlite3
import re
from typing import Type, Dict, List, Tuple
from configparser import ConfigParser


_log = logging.getLogger(__name__)


_CREATE_LOG = """CREATE TABLE log(
    id INTEGER PRIMARY KEY,
    on_air TEXT NOT NULL,
    artist TEXT,
    title TEXT,
    album TEXT,
    source TEXT,
    initial_uri TEXT
);
"""

_CREATE_IDX_LOG_ON_AIR = "CREATE INDEX idx_log_on_air ON log(on_air);"

_CREATE_LOG_EXTRA = """CREATE TABLE log_extra(
    log_id INTEGER REFERENCES log(id) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);"""

def install_metadata_db(config:Type[ConfigParser]):
    with MetadataDB(config) as db:
        columns = db.execute("PRAGMA table_info(log);").fetchall()
        if columns:
            pass # place future updates here
        else:
            db.execute(_CREATE_LOG)

        columns = db.execute("PRAGMA index_info(idx_log_on_air);").fetchall()
        if columns:
            pass # place future updates here
        else:
            db.execute(_CREATE_IDX_LOG_ON_AIR)

        columns = db.execute("PRAGMA table_info(log_extra);").fetchall()
        if columns:
            pass # place future updates here
        else:
            db.execute(_CREATE_LOG_EXTRA)


class MetadataDB(object):
    """
    A context manager providing an SQLite connection to the ``metadata_log`` DB,
    where foreign key constraints are enabled.
    It commits and closes the DB when exiting the context.
    """
    def __init__(self, config:Type[ConfigParser]):
        self._connection = sqlite3.connect(config['metadata_log']['db'])

    def __enter__(self) -> Type[sqlite3.Connection]:
        self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def __exit__(self, type, value, traceback):
        self._connection.commit()
        self._connection.close()


class FieldFilter(object):
    # this is a lazy implementation of a singleton ; in the same program it
    # will always be called with the same config object, so we don't need much
    # thread-safety

    _fields = None
    _wildcards = None

    @classmethod
    def _load(cls, config):
        raw = config['metadata_log']['ignore_fields']
        splitted = raw.split(',')
        # we ignore at least fields from the log table
        fields = set(['on_air', 'artist', 'title', 'album', 'source', 'initial_uri'])
        wildcards = list()
        for entry in splitted:
            if '*' in entry:
                wildcards.append(re.compile(entry.strip().replace('*', '.*')))
            else:
                fields.add(entry.strip())
        cls._fields = fields
        cls._wildcards = wildcards
        _log.debug("Will ignore metadata fields %r", fields)
        _log.debug("Will ignore medadata fields matching %r", wildcards)

    @classmethod
    def filter(cls, config:Type[ConfigParser], data:Dict) -> List[Tuple[str, str]]:
        """
        Extracts metadata entries that fit in our ``log_extra`` table.
        Parameter:
            config: daemon configuration ; we search for ``ignore_fields`` in the ``metadata_log`` section.
            data: as provided by Liquidsoap
        Returns:
            A list of ``(key, value)`` couples, for each key in the input
            dictionary that is not included in ``ignore_fields`` or in the main
            ``log`` table.
        """
        if cls._fields is None:
            cls._load(config)
        result = list()
        for k, v in data.items():
            if k in cls._fields:
                pass
            elif any(rule.match(k) for rule in cls._wildcards):
                pass
            else:
                result.append((k, v))
        return result


def save_metadata(config:Type[ConfigParser], data:Dict):
    """
    Save the metadata provided by Liquidsoap.

    Fields that do not fit into our ``log`` table are saved to ``log_extra``,
    except those matching one in the ``ignore_fields`` configuration.
    Empty values are not saved.
    When ``initial_uri`` is not provided by Liquidsoap, we might use
    ``source_url`` instead (this may happen for example from ``http.input``).
    """
    with MetadataDB(config) as db:
        log_fields = ['on_air']
        try:
            log_values = (data['on_air'], )
        except KeyError:
            raise ValueError("Metadata should at least contain on_air")

        for column in ['artist', 'title', 'album', 'source', 'initial_uri']:
            if data.get(column):
                log_fields.append(column)
                log_values += (data[column], )
        if not data.get('initial_uri') and data.get('source_url'):
            log_fields.append('initial_uri')
            log_values += (data['source_url'], )

        query = "INSERT INTO log (%s) VALUES (%s)" % (
            ', '.join(log_fields), ', '.join(['?'] * len(log_fields))
        )
        cursor = db.execute(query, log_values)
        log_id = cursor.lastrowid

        extra = FieldFilter.filter(config, data)
        query = "INSERT INTO log_extra (log_id, key, value) VALUES (%d, ?, ?)" % log_id
        db.executemany(query, extra)
