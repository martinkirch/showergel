import unittest
from datetime import datetime, timedelta

from showergel import scheduler
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
        self.app.delete('/schedule/', status=405)
        self.app.delete('/schedule/2020-07-19T16:56:29', status=404)

    def test_basic_scheduler_api(self):
        tomorrow = (datetime.now() + timedelta(days=1.)).isoformat()
        help_tomorrow = {
            'command': 'help',
            'when': tomorrow,
        }
        result = self.app.put_json('/schedule', help_tomorrow).json
        event_id = result['event_id']
        self.app.put_json('/schedule', help_tomorrow, status=409)

        schedule = self.app.get('/schedule').json['schedule']
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]['event_id'], event_id)
        self.assertEqual(schedule[0]['command'], help_tomorrow['command'])
        # APS adds timezone info so we just test the datetime part of "when"
        self.assertTrue(schedule[0]['when'].startswith(help_tomorrow['when']))

        self.app.delete('/schedule/'+event_id)
        schedule = self.app.get('/schedule').json['schedule']
        self.assertEqual(len(schedule), 0)

if __name__ == '__main__':
    unittest.main(failfast=True)
