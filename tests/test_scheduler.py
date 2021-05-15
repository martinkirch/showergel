import unittest
from datetime import datetime, timedelta
from . import ShowergelTestCase

from showergel.scheduler import Scheduler

class TestScheduler(ShowergelTestCase):

    def test_commands_scheduling(self):
        scheduler = Scheduler.get()
        with self.assertRaises(ValueError):
            scheduler.command("", datetime.now())

        with self.assertRaises(ValueError):
            scheduler.command("help", datetime.now() - timedelta(days=1.))

        tomorrow = datetime.now() + timedelta(days=1.)
        scheduler.command("help", tomorrow)
        with self.assertRaises(ValueError):
            scheduler.command("help", tomorrow)

if __name__ == '__main__':
    unittest.main(failfast=True)
