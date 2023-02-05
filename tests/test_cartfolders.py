# TODO
# - unit test Cart()
#  -- check logging by re-creating CartFolders: ensure next() is correct too (will require stubbing Log entries)
# - simple API test
from tempfile import TemporaryDirectory
from os.path import join, isdir
from os import mkdir
import time

from showergel.cartfolders import CartFolders, EmptyCartException

from . import ShowergelTestCase, DBSession, APP_CONFIG


class CartFoldersTestCase(ShowergelTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpdir = TemporaryDirectory()
        APP_CONFIG['cartfolders'] = {
            'testcart': join(cls.tmpdir.name, "cartfolder"),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.tmpdir.cleanup()
        del APP_CONFIG['cartfolders']

    def test_cart(self):
        """
        Unit test ``Cart`` and ``CartFolders``.
        """
        dbsession = DBSession()
        cart_folders = CartFolders(dbsession, APP_CONFIG)

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

        # ensure event handlers are done scanning the folder
        time.sleep(0.1)

        self.assertEqual(pattern + "A", cart_folders['testcart'].next())
        self.assertEqual(pattern + "B", cart_folders['testcart'].next())
        self.assertEqual(pattern + "C", cart_folders['testcart'].next())
        self.assertEqual(pattern + "A", cart_folders['testcart'].next())
        self.assertEqual(pattern + "B", cart_folders['testcart'].next())
        self.assertEqual(pattern + "C", cart_folders['testcart'].next())
        self.assertEqual(pattern + "A", cart_folders['testcart'].next())

        # last thing before ending the test
        cart_folders.stop_watching()
