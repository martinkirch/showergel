import arrow
from . import ShowergelTestCase


class TestLive(ShowergelTestCase):

    def test_get_live(self):
        before = arrow.now()
        resp = self.app.get('/live').json

        server_time = arrow.get(resp['server_time'])
        self.assertLessEqual(before, server_time)
        self.assertLessEqual(server_time, arrow.now())
        self.assertIn('source', resp)
        self.assertIn('on_air', resp)
        self.assertIn('status', resp)

    def test_get_parameters(self):
        resp = self.app.get('/parameters').json
        self.assertEqual(resp['name'], "ShowergelTest")
        self.assertIn('version', resp)
        self.assertIsInstance(resp['commands'], list)
        self.assertEqual(resp['liquidsoap_version'], "Stub")

    def test_skip(self):
        resp = self.app.get('/live').json
        previous_source = resp['source']
        self.app.delete('/live')
        resp = self.app.get('/live').json
        self.assertNotEqual(resp['source'], previous_source)
