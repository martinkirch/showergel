"""
============
Cart folders
============

Showergel lets you configure _cart folders_. A cart is a file-system folder
watched by Showergel so it can work as a playlist. A cart can be
scheduled regularly from Showergel's _Schedule_ tab, so at given time
Showergel will play one file, 
Reset when touching *anything* in the folder (without any effect on what's currently on air).
But if nothing moves, Showergel will ensure that files will be broadcasted in the intended order. 

Cart folders have been introduced because of the following use case:
when a folder is pre-loaded with a dozen episodes of a weekly show,
if the machine reboots next month the cart will still play episodes by ascending file name.
This is a major difference with Liquidsoap's ``playlist(mode="normal")`` source,
which restarts from the first file in folder after a reboot.

When a file is played, it is added to a Liquidsoap queue, whose name is configured in liquidsoap.cartfolders_queue
Also how to configure cart folders' paths.
If the folder does not exists it will be created.
Show an extract of the conf.

Warning block: sub-folders will *not* be considered. Put only media files in cart folders.

Also give some examples.
discuss track-sensitiveness issues
"""
from __future__ import annotations
import logging
from os import scandir, makedirs

from sqlalchemy.orm import Session
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import arrow

from showergel.liquidsoap_connector import Connection
from showergel.metadata import Log

_log = logging.getLogger(__name__)

class EmptyCartException(Exception):
    """
    Raised by ``Cart.next()`` when the cart is empty
    """

RELOAD_INITIAL_URI = '__cart reload__'

class Cart:
    def __init__(self, path) -> None:
        self.path = path
        makedirs(path, exist_ok=True)
        self.current = -1
        self.content = []

    def next(self) -> str:
        """
        Return path to the next file we should play.
        Might raise ``EmptyCartException``.
        """
        if not self.content:
            raise EmptyCartException()
        nextpath = self.content[self.current]
        self.current += 1
        if self.current == len(self.content):
            self.current = 0
        return nextpath

    def reload_content(self):
        """
        This method resets the cart folder by updating its content according
        to files in folder and resetting the current file marker.
        Sub-folders are ignored, and files are remembered by ascending file name.

        Must be called upon start or change in the folder.
        """
        self.content = []
        for direntry in scandir(self.path):
            if direntry.is_file() and not direntry.name.startswith('.'):
                self.content.append(direntry.path)
        self.content.sort()
        self.current = 0

    def find_current_from_log(self, dbsession:Session):
        if not self.content:
            return
        latest = (dbsession.query(Log)
            .filter(Log.source == CartFolders.liquidsoap_queue)
            .filter(
                Log.initial_uri.in_(self.content) |
                (Log.initial_uri == RELOAD_INITIAL_URI))
            .order_by(Log.on_air.desc())
            .first()
        )
        if latest and latest.initial_uri != RELOAD_INITIAL_URI:
            self.current = self.content.index(latest.initial_uri)
            self.next()

    def log_reload(self, dbsession:Session):
        dbsession.add(Log(
            on_air=arrow.utcnow().datetime,
            source=CartFolders.liquidsoap_queue,
            initial_uri=RELOAD_INITIAL_URI,
        ))
        dbsession.flush()

class CartReloadingHandler(FileSystemEventHandler):
    def __init__(self, name, cart:Cart, dbsession:Session) -> None:
        self.name = name
        self.cart = cart
        self.dbsession = dbsession
        super().__init__()

    def on_any_event(self, event):
        self.cart.reload_content()
        self.cart.log_reload(self.dbsession)

class CartFolders:
    """
    Only one instance of this class should exist in the Showergel process:
    call :ref:`setup` once, then access the instance with :ref:`get`.
    """

    __instance = None

    @classmethod
    def setup(cls, dbsession:Session, config:dict) -> CartFolders:
        """
        This should be called once, when starting the program.
        """
        cls.__instance = cls(dbsession, config)
        try:
            cls.liquidsoap_queue = config['liquidsoap']['cartfolders_queue']
        except KeyError:
            _log.warning("Missing 'cartfolders_queue' in the [liquidsoap] section of the configuration.")
            cls.liquidsoap_queue = None
        return cls.__instance

    @classmethod
    def get(cls) -> CartFolders:
        """
        This is the only accessor of the programs's ``CartFolders`` instance.
        Return:
            (CartFolders):
        """
        if not cls.__instance:
            raise ValueError("CartFolders.setup() has not been called yet")
        return cls.__instance

    @classmethod
    def test_reset(cls):
        """
        This should only be used when unit testing, to ensure updates are not
        triggered when the test folder is cleaned up
        """
        cls.__instance.observer.stop()
        cls.__instance = None

    def __init__(self, dbsession:Session, config:dict):
        if 'cartfolders' not in config:
            return
        self.observer = Observer()
        self._carts = {}
        for name, path in config['cartfolders'].items():
            cart = Cart(path)
            cart.reload_content()
            cart.find_current_from_log(dbsession)
            self._carts[name] = cart
            handler = CartReloadingHandler(name, self._carts[name], dbsession)
            self.observer.schedule(handler, cart.path)

        self.observer.start()

    def __getitem__(self, cartname:str) -> Cart:
        return self._carts[cartname]


def do_enqueue_cart(cartname):
    """
    Function called each time a cart is scheduled. Pushes the next file to queue.
    """
    if not CartFolders.liquidsoap_queue:
        return
    try:
        nextpath = CartFolders.get()[cartname].next()
    except KeyError:
        _log.critical("A cart called %s has been scheduled now, but does not appear in Showergel's configuration. Please clean the schedule.", cartname)
        return
    except EmptyCartException:
        _log.info("Cart %s should play now, but its folder is empty", cartname)
        return
    connection = Connection.get()
    command = f"{CartFolders.liquidsoap_queue}.push {nextpath}"
    _log.debug("Enqueuing cart folder: %s", command)
    result = connection.command(command)
    _log.debug("Liquidsoap replied: %s", result)
