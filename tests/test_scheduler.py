import unittest
import time
from datetime import datetime, timedelta
import arrow
from tests import ShowergelTestCase
from showergel.scheduler import Scheduler

class TestScheduler(ShowergelTestCase):

    def test_scheduler(self):
        scheduler = Scheduler.get()
        with self.assertRaises(ValueError):
            scheduler.command("", datetime.utcnow())

        with self.assertRaises(ValueError):
            scheduler.command("help", datetime.utcnow() - timedelta(days=1.))

        tomorrow = datetime.now() + timedelta(days=1.)
        scheduler.command("help", tomorrow)
        with self.assertRaises(KeyError):
            scheduler.command("help", tomorrow)

    def test_invalid_requests(self):
        self.app.put_json('/schedule', {}, status=400)
        when = arrow.now().shift(hours=1)
        self.app.put_json('/schedule', {
            'command': '',
            'when': when.isoformat(),
        }, status=400)
        self.app.put_json('/schedule', {
            'command': 'help',
            'when': when.shift(days=-1).isoformat(),
        }, status=400)
        self.app.put('/schedule', status=400)
        self.app.delete('/schedule/', status=405)
        self.app.delete('/schedule/2020-07-19T16:56:29', status=404)

    def test_basic_scheduler_api(self):
        tomorrow = arrow.now().shift(days=1)
        help_tomorrow = {
            'command': 'help',
            'when': tomorrow.isoformat(),
        }
        result = self.app.put_json('/schedule', help_tomorrow).json
        event_id = result['event_id']
        self.app.put_json('/schedule', help_tomorrow, status=409)

        schedule = self.app.get('/schedule').json['schedule']
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]['event_id'], event_id)
        self.assertEqual(schedule[0]['command'], help_tomorrow['command'])
        self.assertEqual(tomorrow, arrow.get(schedule[0]['when']))

        self.app.delete('/schedule/'+event_id)
        schedule = self.app.get('/schedule').json['schedule']
        self.assertEqual(len(schedule), 0)

    def test_commands_are_logged(self):
        now = arrow.now()
        right_now = arrow.now().shift(seconds=0.5)
        command = "help blablablalba"
        posted = self.app.put_json('/schedule', {
            'command': command,
            'when': right_now.isoformat(),
        }).json
        time.sleep(1) #sorry
        logged = self.app.get('/metadata_log', {'start': now.isoformat()}).json['metadata_log']
        self.assertEqual(logged[0]['source'], "showergel_scheduler")
        self.assertEqual(logged[0]['initial_uri'], command)
        self.assertLess(arrow.get(logged[0]['on_air']) - right_now, timedelta(milliseconds=10.))

if __name__ == '__main__':
    unittest.main(failfast=True)
