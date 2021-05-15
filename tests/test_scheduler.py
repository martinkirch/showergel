import unittest
from datetime import datetime, timedelta
from . import ShowergelTestCase

from showergel.scheduler import Scheduler

class TestScheduler(ShowergelTestCase):

    def test_scheduler(self):
        scheduler = Scheduler.get()
        with self.assertRaises(ValueError):
            scheduler.command("", datetime.now())

        with self.assertRaises(ValueError):
            scheduler.command("help", datetime.now() - timedelta(days=1.))

        tomorrow = datetime.now() + timedelta(days=1.)
        scheduler.command("help", tomorrow)
        with self.assertRaises(KeyError):
            scheduler.command("help", tomorrow)

    def test_invalid_requests(self):
        self.app.put_json('/schedule', {}, status=400)
        self.app.put_json('/schedule', {
            'command': '',
            'when': (datetime.now() - timedelta(days=1.)).isoformat(),
        }, status=400)
        self.app.put('/schedule', status=400)

    def test_basic_scheduler_api(self):
        tomorrow = (datetime.now() + timedelta(days=1.)).isoformat()
        help_tomorrow = {
            'command': 'help',
            'when': tomorrow,
        }
        result = self.app.put_json('/schedule', help_tomorrow).json
        self.assertIn('event_id', result)
        self.app.put_json('/schedule', help_tomorrow, status=409)

if __name__ == '__main__':
    unittest.main(failfast=True)
