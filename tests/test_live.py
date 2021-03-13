from datetime import datetime
from . import ShowergelTestCase


class TestLive(ShowergelTestCase):

    def test_get_live(self):
        before = datetime.now()
        resp = self.app.get('/live')
        server_time = datetime.fromisoformat(resp.json['server_time'])
        self.assertLessEqual(before, server_time)
        self.assertLessEqual(server_time, datetime.now())
