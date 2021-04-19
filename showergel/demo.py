"""
This module contains everything about the demo mode
"""

import random
from datetime import datetime, timedelta
from typing import Type

from sqlalchemy.orm import sessionmaker

from showergel.users import User
from showergel.metadata import Log

try:
    with open("/usr/share/dict/words") as words_file:
        WORDS = words_file.read().splitlines()
except FileNotFoundError:
    WORDS = "lorem ipsum dolor sit amet consectetur adipiscing elit aenean ultrices augue in neque tincidunt cursus aenean non turpis odio integer porttitor ipsum feugiat orci lobortis eu varius nulla pulvinar ut non enim massa qliquam at eros quis orci luctus facilisis quisque quis pulvinar mi proin nisl nibh vehicula at risus vitae porttitor ornare purus".split()

def artistic_generator():
    return ' '.join([WORDS[random.randint(0, len(WORDS)-1)] for i in range(2)])

def stub_log_data(session, config):
    tracktime = timedelta(minutes=3)
    now = datetime.now()

    sources = ['test', 'live', 'unknwon_sound_source1231']
    albums = ['Showergel Rocks', 'Better hygiene with Liquidsoap']

    # generate a few days of log:
    for i in range(3000):
        now -= tracktime
        title = artistic_generator()
        artist = artistic_generator()
        album = albums[i % len(albums)]
        filename = f"/home/radio/Music/{album}/" +\
            artist.replace(' ', '_') + '-' + title.replace(' ', '_') + '.flac'
        Log.save_metadata(config, session, {
            'on_air': now.isoformat(),
            'artist': artist,
            'title': title,
            'source': sources[i % len(sources)],
            'initial_uri': filename,
            'album': album,
            'editor': "Pytest",
            'year': now.year - (i % 10),
            'tracknumber': i % 8,
        })

def stub_users(session):
    User.create(session, "tester", "verysecret")
    User.create(session, "Radio Showergel", "yayradi0")
    User.create(session, "Debuggers", "blablabla")

def stub_all(engine, config):
    from showergel.db import Base
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    stub_users(session)
    stub_log_data(session, config)
    session.commit()
    session.close()

class FakeLiquidsoapConnector:
    """
    mocks ``TelnetConnector`` when no configuration exists at all - as in unit tests.

    returns something different each time it's called.
    """

    FAKE_TIME_SHIFT = timedelta(minutes=3)

    def __init__(self):
        self._uptime = timedelta(hours=10)
        now = datetime.now().replace(microsecond=0)
        self._on_air = now - self._uptime
        self._i = 0

    def uptime(self) -> Type[timedelta]:
        self._uptime += self.FAKE_TIME_SHIFT
        return self._uptime

    def skip(self):
        pass

    def remaining(self):
        return self.FAKE_TIME_SHIFT.total_seconds()

    def current(self) -> dict:
        metadata = self.generate_metadata()
        metadata["uptime"] = str(self.uptime())
        self._on_air += self.FAKE_TIME_SHIFT
        metadata["on_air"] = self._on_air.isoformat()
        return metadata

    def generate_metadata(self) -> dict:
        """
        generates something different each call
        """
        sources = ['test', 'live', 'unkown_sound_source1231']
        albums = ['Showergel Rocks', 'Better hygiene with Liquidsoap']

        self._i += 1
        title = artistic_generator()
        artist = artistic_generator()
        album = albums[self._i % len(albums)]
        filename = f"/home/radio/Music/{album}/" +\
            artist.replace(' ', '_') + '-' + title.replace(' ', '_') + '.flac'
        return {
            'artist': artist,
            'title': title,
            'source': sources[self._i % len(sources)],
            'status': 'simulating',
            'initial_uri': filename,
            'album': album,
            'editor': "Pytest",
            'year': self._on_air.year - (self._i % 10),
            'tracknumber': self._i % 8,
        }

class DemoLiquidsoapConnector(FakeLiquidsoapConnector):
    """
    mocks ``TelnetConnector`` for demo mode. It takes clock time into account,
    to simulate 3-minutes tracks

    Enable it with the following configuration:

    .. code-block:: ini
        [liquidsoap]
        method = demo
    """

    TRACK_LENGTH = timedelta(minutes=3)

    def __init__(self):
        super().__init__()
        self._started_at = datetime.now().replace(microsecond=0)
        self._metadata = self.generate_metadata()

    def skip(self):
        self._on_air = datetime.now().replace(microsecond=0)
        self._metadata = self.generate_metadata()

    def uptime(self) -> Type[timedelta]:
        uptime = datetime.now().replace(microsecond=0) - self._started_at
        if (datetime.now() - self._on_air) >= self.TRACK_LENGTH:
            self.skip()
        return uptime

    def current(self) -> dict:
        # call uptime() first because it might update ._metadata
        uptime = str(self.uptime())
        metadata = dict(self._metadata)
        metadata["uptime"] = uptime
        metadata["on_air"] = self._on_air.isoformat()
        return metadata

    def remaining(self):
        return max(0.0, (self.TRACK_LENGTH - (datetime.now() - self._on_air)).total_seconds())

# test tool
if __name__ == '__main__':
    conn = FakeLiquidsoapConnector()
    import time
    while True:
        print(conn.current())
        time.sleep(1.)
