from tempfile import TemporaryDirectory
from os.path import join, isdir, split
from os import mkdir, remove
import time
from datetime import timedelta

import arrow

from showergel.cartfolders import CartFolders, EmptyCartException
from showergel.metadata import Log, LogExtra

from . import ShowergelTestCase, DBSession, APP_CONFIG


class CartFoldersTestCase(ShowergelTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpdir = TemporaryDirectory()
        APP_CONFIG['cartfolders'] = {
            'testcart': join(cls.tmpdir.name, "cartfolder"),
        }
        cls.session = DBSession()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.tmpdir.cleanup()
        del APP_CONFIG['cartfolders']
        cls.session.query(LogExtra).delete()
        cls.session.query(Log).delete()

    def stub_playout(self, path):
        _, filename = split(path)
        self.session.add(Log(
            on_air = arrow.utcnow().datetime,
            artist = "UnitTest",
            title = filename,
            album = "CartFoldersTestCase",
            source = APP_CONFIG['liquidsoap']['cartfolders_queue'],
            initial_uri = path,
        ))
        self.session.flush()


    def test_cart(self):
        """
        Unit test ``Cart`` and ``CartFolders``.
        """
        cart_folders = CartFolders.setup(self.session, APP_CONFIG)
        try:
            self.assertTrue(isdir(APP_CONFIG['cartfolders']['testcart']))

            with self.assertRaises(EmptyCartException):
                _ = cart_folders['testcart'].next()

            # creating fake media files should be enough to refresh cart's content
            pattern = join(APP_CONFIG['cartfolders']['testcart'], "file")
            tmp = open(pattern + "A", 'w')
            tmp.close()
            tmp = open(pattern + "B", 'w')
            tmp.close()
            tmp = open(pattern + "C", 'w')
            tmp.close()
            # these should be ignored:
            tmp = open(join(APP_CONFIG['cartfolders']['testcart'], ".fileA~"), 'w')
            tmp.close()
            mkdir(join(APP_CONFIG['cartfolders']['testcart'], "subfolder"))

            time.sleep(0.1) # ensure event handlers are done scanning the folder

            self.assertEqual(pattern + "A", cart_folders['testcart'].next())
            self.stub_playout(pattern + "A")
            self.assertEqual(pattern + "B", cart_folders['testcart'].next())
            self.stub_playout(pattern + "B")
            self.assertEqual(pattern + "C", cart_folders['testcart'].next())
            self.stub_playout(pattern + "C")
            self.assertEqual(pattern + "A", cart_folders['testcart'].next())
            self.stub_playout(pattern + "A")
            self.assertEqual(pattern + "B", cart_folders['testcart'].next())
            self.stub_playout(pattern + "B")
            self.assertEqual(pattern + "C", cart_folders['testcart'].next())
            self.stub_playout(pattern + "C")
            self.assertEqual(pattern + "A", cart_folders['testcart'].next())
            self.stub_playout(pattern + "A")

            # simulate Showergel rebooting
            CartFolders.test_reset()
            cart_folders = CartFolders.setup(self.session, APP_CONFIG)
            self.assertEqual(pattern + "B", cart_folders['testcart'].next())
            self.stub_playout(pattern + "B")
            self.stub_playout(pattern + "C")
            CartFolders.test_reset()
            cart_folders = CartFolders.setup(self.session, APP_CONFIG)
            self.assertEqual(pattern + "A", cart_folders['testcart'].next())
            self.stub_playout(pattern + "A")

            # touching something in the folder + reboot
            remove(pattern + "C")
            time.sleep(0.1) # ensure event handlers are done scanning the folder
            CartFolders.test_reset()
            cart_folders = CartFolders.setup(self.session, APP_CONFIG)
            self.assertEqual(pattern + "A", cart_folders['testcart'].next())

        finally:
            # turn off the watch because test cleanup could trigger callbacks
            CartFolders.test_reset()
