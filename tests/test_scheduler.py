import unittest
import time
from datetime import datetime, timedelta
import arrow

from showergel.cartfolders import CartFolders
from showergel.scheduler import Scheduler

from tests import ShowergelTestCase, DBSession

class TestScheduler(ShowergelTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session = DBSession()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        CartFolders.test_reset()

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
        self.app.put_json('/schedule/command', {}, status=400)
        self.app.put_json('/schedule/cartfolder', {}, status=400)
        when = arrow.now().shift(hours=1)
        self.app.put_json('/schedule/command', {
            'command': '',
            'when': when.isoformat(),
        }, status=400)
        self.app.put_json('/schedule/command', {
            'command': 'help',
            'when': when.shift(days=-1).isoformat(),
        }, status=400)
        self.app.put('/schedule', status=405)
        self.app.delete('/schedule/', status=405)
        self.app.delete('/schedule/2020-07-19T16:56:29', status=404)

    def test_basic_scheduler_api(self):
        tomorrow = arrow.now().shift(days=1)
        help_tomorrow = {
            'command': 'help',
            'when': tomorrow.isoformat(),
        }
        result = self.app.put_json('/schedule/command', help_tomorrow).json
        event_id = result['event_id']
        self.app.put_json('/schedule/command', help_tomorrow, status=409)
        self.assertEqual(result['type'], "command")
        self.assertEqual(result['what'], help_tomorrow['command'])
        self.assertEqual(arrow.get(result['when']), tomorrow)

        schedule = self.app.get('/schedule').json
        self.assertEqual(len(schedule), 1)
        (when, event) = schedule.popitem()
        self.assertEqual(event['event_id'], event_id)
        self.assertEqual(event['type'], "command")
        self.assertEqual(event['what'], help_tomorrow['command'])
        self.assertEqual(tomorrow, arrow.get(when))

        self.app.delete('/schedule/'+event_id)
        schedule = self.app.get('/schedule').json
        self.assertEqual(len(schedule), 0)

    def test_commands_are_logged(self):
        now = arrow.now()
        right_now = arrow.now().shift(seconds=0.5)
        command = "help blablablalba"
        _ = self.app.put_json('/schedule/command', {
            'command': command,
            'when': right_now.isoformat(),
        }).json
        time.sleep(1) #sorry
        logged = self.app.get('/metadata_log', {'start': now.isoformat()}).json['metadata_log']
        self.assertEqual(logged[0]['source'], "showergel_scheduler")
        self.assertEqual(logged[0]['initial_uri'], command)
        self.assertLess(arrow.get(logged[0]['on_air']) - right_now, timedelta(milliseconds=10.))

    def test_cartfolder_scheduling(self):
        params = {
            'name': 'thiscartdoesnotexists',
            'day_of_week': 0,
            'hour': 12,
            'minute': 0,
            'timezone': 'Europe/Paris',
        }
        self.app.put_json('/schedule/cartfolder', params, status=400).json

        params = {
            'name': 'testcart',
            'day_of_week': 0,
            'hour': 12,
            'minute': 0,
            'timezone': 'Europe/Paris',
        }
        result = self.app.put_json('/schedule/cartfolder', params).json
        self.assertEqual(result['type'], "cartfolder")
        self.assertEqual(result['what'], params['name'])
        event_id = result['event_id']

        self.app.put_json('/schedule/cartfolder', params, status=409).json

        # TODO add an option for odd/even weeks, or N-th weekday of the month, see https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html#expression-types
        # TODO schedule another cartfolder, then remove it from the configuration: should be highlighted in calendar, with a help message

        schedule = self.app.get('/schedule').json
        self.assertEqual(len(schedule), 1)
        event = schedule.popitem()[1]
        self.assertEqual(event['type'], "cartfolder")
        self.assertEqual(event['event_id'], event_id)
        self.assertEqual(event['what'], 'testcart')

        self.app.delete('/schedule/'+event_id)


if __name__ == '__main__':
    unittest.main(failfast=True)
