"""
===============
Metadata logger
===============

This module contains functions that process and store the metadata of tracks
played by Liquidsoap.
"""

import sqlite3
from typing import Type
from configparser import ConfigParser


_CREATE_LOG = """CREATE TABLE log(
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
    log_id INTEGER REFERENCES log(rowid) ON UPDATE CASCADE ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL
);"""

def install_metadata_db(conf:Type[ConfigParser]):
    with MetadataDB(conf) as db:
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
    A context manager providing an SQLite connection to the ``metadata_log`` DB.
    It commits and closes the DB when exiting the context.

    Parameters:
        conf: as provided by ``ConfigParser``
    """
    def __init__(self, config:Type[ConfigParser]):
        self._connection = sqlite3.connect(config['metadata_log']['db'])

    def __enter__(self) -> Type[sqlite3.Connection]:
        return self._connection

    def __exit__(self, type, value, traceback):
        self._connection.commit()
        self._connection.close()

## TODO : when saving metadata, transform source_url into initial_uri
