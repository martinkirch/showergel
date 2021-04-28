from datetime import datetime, timedelta
from showergel.metadata import LIQUIDSOAP_DATEFORMAT, LogExtra, FieldFilter
from showergel.demo import artistic_generator
from . import ShowergelTestCase, DBSession, app

FIELD_FILTER_CONFIG = {
    'metadata_log.extra_fields': ["lyrics", "mb*"],
}

class TestMetadataLog(ShowergelTestCase):

    def test_field_filter(self):
        """
        this should be the first test running in this case
        """

        # FieldFilter misses its configuration:
        with self.assertRaises(ValueError):
            FieldFilter.filter({
                "title": "Greatest song in the world",
                "lyrics": "lorem ipsum",
            })

        # when disabling `only_extra`, title should be included
        filtered = dict(FieldFilter.filter({
            "title": "Greatest song in the world",
            "lyrics": "lorem ipsum",
            "mb_trackid": "cb4c28fe-0cfb-4f9f-8546-209088441c92",
            "genre": "Test",
        }, config=FIELD_FILTER_CONFIG, only_extra=False))
        self.assertIn('title', filtered)
        self.assertIn('lyrics', filtered)
        self.assertIn('mb_trackid', filtered)
        self.assertNotIn('genre', filtered)

        # don't crash if configuration misses FieldFilter's params
        FieldFilter.setup({})
        _ = FieldFilter.filter({
            "title": "Greatest song in the world",
            "lyrics": "lorem ipsum",
        }, only_extra=False)

        # leave the normal conf for other tests
        FieldFilter.setup(app.config)

    def test_metadata_log(self):
        # at least on_air is required
        resp = self.app.post_json('/metadata_log', {}, status=400)

        # don't crash when no JSON is provided
        resp = self.app.post('/metadata_log', status=400)

        tracktime = timedelta(minutes=3)
        now = datetime.now()

        first_track = {
            'on_air': now.strftime(LIQUIDSOAP_DATEFORMAT),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
        }
        resp = self.app.post_json('/metadata_log', first_track)

        # ensure there's nothing in log_extra at this point
        session = DBSession()
        found = session.query(LogExtra).all()
        self.assertEqual(0, len(found))

        now += tracktime
        last = {
            'on_air': now.isoformat(),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
            'source_url': "http://check.its.renamed/to/initial_uri"
        }

        # make it robust to repeated posts...
        resp = self.app.post_json('/metadata_log', last)
        resp = self.app.post_json('/metadata_log', last)
        # ... and especially if a liquidsoap operator reposts old data !
        # we take care of this because many operators (switch, fallback,...)
        # default `replay_metadata` to true
        resp = self.app.post_json('/metadata_log', first_track)

        logged = self.app.get('/metadata_log').json['metadata_log']
        self.assertEqual(2, len(logged))
        # also check source_url is used as initial_uri
        last['initial_uri'] = last['source_url']
        del last['source_url']
        self.assertDictEqual(last, logged[0])

        before_track3 = now
        now += tracktime
        last = {
            'on_air': now.isoformat(),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
        }
        resp = self.app.post_json('/metadata_log', last)

        logged = self.app.get('/metadata_log', {
            "chronological": True,
            "limit": 2,
        }).json['metadata_log']
        self.assertEqual(2, len(logged))
        for log in logged:
            on_air = datetime.fromisoformat(log["on_air"])
            self.assertLessEqual(on_air, before_track3)

        logged = self.app.get('/metadata_log', {
            "start": before_track3.isoformat(),
        }).json['metadata_log']
        self.assertEqual(2, len(logged))

        logged = self.app.get('/metadata_log', {
            "end": before_track3.isoformat(),
        }).json['metadata_log']
        self.assertEqual(2, len(logged))

        logged = self.app.get('/metadata_log', {
            "start": datetime(2021, 1, 1).isoformat(),
            "end": datetime(2021, 1, 2).isoformat(),
        }).json['metadata_log']
        self.assertEqual(0, len(logged))

        # check that limit is ignored when start and end is provided
        # check start and end can be parsed as YYYY-MM-DD
        logged = self.app.get('/metadata_log', {
            "limit": 1,
            "start": datetime(2021, 1, 1).strftime(r"%Y-%m-%d"),
            "end": (now + tracktime).isoformat(),
        }).json['metadata_log']
        self.assertEqual(3, len(logged))

        # put some data to LogExtra... and get it back
        # this is tied to the configuration in tests/__init__.py
        now += tracktime
        last = {
            'on_air': now.isoformat(),
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
            'editor': 'Pytest',
            'tracknumber': 1,
        }
        resp = self.app.post_json('/metadata_log', last)

        logged = self.app.get('/metadata_log', {
            "limit": 1,
        }).json['metadata_log'][0]
        self.assertNotIn('editor', logged)
        self.assertEqual(logged['tracknumber'], '1')
