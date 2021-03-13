"""
This module contains everything about the demo mode
"""

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker

from showergel.users import User
from showergel.metadata import Log

with open("/usr/share/dict/words") as words_file:
    WORDS = words_file.read().splitlines()

def artistic_generator():
    return ' '.join([WORDS[random.randint(0, len(WORDS))] for i in range(2)])

def stub_log_data(session, config):
    tracktime = timedelta(minutes=3)
    now = datetime.now()

    sources = ['test', 'live', 'unknwon_sound_source1231']
    albums = ['Showergel Rocks', 'Better hygiene with Liquidsoap']

    for i in range(50):
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
    from showergel import Base
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    stub_users(session)
    stub_log_data(session, config)
    session.commit()
    session.close()
