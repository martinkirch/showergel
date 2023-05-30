import arrow

from showergel.metadata import Log, LogExtra, FieldFilter
from showergel.demo import artistic_generator
from showergel.liquidsoap_connector import Connection
from . import ShowergelTestCase, DBSession, app

FIELD_FILTER_CONFIG = {
    'metadata_log.extra_fields': ["lyrics", "mb*"],
}

class TestMetadataLog(ShowergelTestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        session = DBSession()
        session.query(LogExtra).delete()
        session.query(Log).delete()

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
        """
        This also test the coupling with (stubbed) ``LiquidsoapConnector.current()``.
        """
        connection = Connection.get()

        # don't crash when no JSON is provided or empty
        resp = self.app.post_json('/metadata_log', {}, status=400)
        resp = self.app.post('/metadata_log', status=400)

        first_track = {
            'artist': artistic_generator(),
            'title': artistic_generator(),
            'source': 'test',
        }
        resp = self.app.post_json('/metadata_log', first_track)

        # make it robust to repeated posts...
        resp = self.app.post_json('/metadata_log', first_track)
        # we take care of this because many operators (switch, fallback,...)
        # default `replay_metadata` to true

        # ensure there's nothing in log_extra at this point - our generated
        # artist/title don't match the ones from LiquidsoapConnector.current(),
        # it should have inserted ``tracknumber`` otherwise
        session = DBSession()
        found = session.query(LogExtra).all()
        self.assertEqual(0, len(found))

        current = connection.current()
        del(current['initial_uri'])
        current['source_url'] = "http://check.its.renamed/to/initial_uri"
        resp = self.app.post_json('/metadata_log', current)

        logged = self.app.get('/metadata_log').json['metadata_log']
        self.assertEqual(2, len(logged))
        self.assertEqual(arrow.get(current['on_air'], tzinfo='local').to('utc'), arrow.get(logged[0]['on_air']))
        self.assertEqual(current['title'], logged[0]['title'])
        self.assertEqual(current['artist'], logged[0]['artist'])
        self.assertEqual(current['source'], logged[0]['source'])
        # check renaming to initial_uri
        self.assertEqual(current['source_url'], logged[0]['initial_uri'])

        before_track3 = arrow.get(current['on_air'], tzinfo='local').to('utc')
        connection.skip()
        current = connection.current()
        resp = self.app.post_json('/metadata_log', current)

        logged = self.app.get('/metadata_log', {
            "chronological": True,
            "limit": 2,
        }).json['metadata_log']
        self.assertEqual(2, len(logged))
        for log in logged:
            self.assertLessEqual(arrow.get(log["on_air"]), before_track3)

        logged = self.app.get('/metadata_log', {
            "start": before_track3.isoformat(),
        }).json['metadata_log']
        self.assertEqual(2, len(logged))

        logged = self.app.get('/metadata_log', {
            "end": before_track3.isoformat(),
        }).json['metadata_log']
        self.assertEqual(2, len(logged))

        logged = self.app.get('/metadata_log', {
            "start": arrow.Arrow(2021, 1, 1).isoformat(),
            "end": arrow.Arrow(2021, 1, 2).isoformat(),
        }).json['metadata_log']
        self.assertEqual(0, len(logged))

        # check that limit is ignored when start and end is provided
        logged = self.app.get('/metadata_log', {
            "limit": 1,
            "start": "2021-01-01", # check start and end can be parsed as YYYY-MM-DD
            "end": current['on_air'],
        }).json['metadata_log']
        self.assertEqual(3, len(logged))

        # get data back from LogExtra
        # this is tied to the configuration in tests/__init__.py
        connection.skip()
        current = connection.current()
        resp = self.app.post_json('/metadata_log', current)

        logged = self.app.get('/metadata_log', {
            "limit": 1,
        }).json['metadata_log'][0]
        self.assertNotIn('editor', logged)
        self.assertEqual(logged['tracknumber'], current['tracknumber'])

        # check there's no crash when a field is missing and doesn't match our connector's metadata
        connection.skip()
        current = connection.current()
        last = {
            'on_air': current['on_air'],
            'artist': artistic_generator(),
        }
        resp = self.app.post_json('/metadata_log', last)

        # check there's no crash when a field is missing and doesn't match our connector's metadata
        connection.skip()
        current = connection.current()
        last = {
            'on_air': current['on_air'],
            'title': artistic_generator(),
        }
        resp = self.app.post_json('/metadata_log', last)

        connection.skip()
        current = connection.current()
        last = {
            'on_air': current['on_air'],
            'artist': artistic_generator(),
            'title': artistic_generator(),
        }
        resp = self.app.post_json('/metadata_log', last)

        # sometimes Liquidsoap lets huge fields get in the query
        # in that case Bottle blocks and returns 413 Request Entity Too Large
        connection.skip()
        current = connection.current()
        current['apic'] = "like a big big picture in metadata" * 100000
        resp = self.app.post_json('/metadata_log', last)
