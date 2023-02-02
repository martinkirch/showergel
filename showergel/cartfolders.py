"""
============
Cart folders
============

Showergel lets you configure _cart folders_. A cart is a file-system folder
watched by Showergel so it can work as a playlist. A cart can be
scheduled regularly from Showergel's _Schedule_ tab, so at given time
Showergel will play one file, 

Note that those files are added to a Liquidsoap queue, whose name is configured in ...

Also give some examples
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Cart:
    def __init__(self) -> None:
        self.current = -1
        self.content = []
    
    def next(self) -> str:
        return "" # TODO self.content[self.current] with increment and error handling
    

# TODO def a function that will be Scheduler's callback

class CartReloadingHandler(FileSystemEventHandler):
    def __init__(self, name, cart:Cart) -> None:
        self.cart = cart
        self.name = name
        super().__init__()

    def on_any_event(self, event):
        # add to Log "reloaded name"
        # reload cart and reset to 0
        pass

class CartFolders:
    """
    Only one instance of this class should exist in the Showergel process:
    call :ref:`setup` once, then access the instance with :ref:`get`.
    """

    __instance = None
    dbsession = None

    @classmethod
    def setup(cls, dbsession:Session, config:dict):
        """
        This should be called once, when starting the program.
        """
        cls.__instance = cls(config)
        cls.dbsession = dbsession
        cls.config = config

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

    def __init__(self, dbsession:Session, config:dict):
        if 'catfolders' not in config:
            return
        self.observer = Observer()
        self._carts = {}
        for name in config['catfolders']:
            cart = Cart() #TODO - load, and reset to previous track
            self._carts[name] = cart
            self.observer.schedule(CartReloadingHandler(name, self._carts[name]), cart, recursive=True)

        self.observer.start()
