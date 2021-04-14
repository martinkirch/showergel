from datetime import datetime
from . import ShowergelTestCase


class TestLive(ShowergelTestCase):

    def test_get_live(self):
        before = datetime.now()
        resp = self.app.get('/live').json

        server_time = datetime.fromisoformat(resp['server_time'])
        self.assertLessEqual(before, server_time)
        self.assertLessEqual(server_time, datetime.now())
        self.assertIn('source', resp)
        self.assertIn('on_air', resp)
        self.assertIn('status', resp)

    def test_get_parameters(self):
        resp = self.app.get('/parameters').json
        self.assertEqual(resp['name'], "ShowergelTest")
        self.assertIn('version', resp)

    def test_skip(self):
        resp = self.app.get('/live').json
        previous_source = resp['source']
        self.app.delete('/live')
        resp = self.app.get('/live').json
        self.assertNotEqual(resp['source'], previous_source)
