=========
Showergel
=========

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel handles externalized features like logging or scheduling
and provides *locally* a Web interface.

**The project is still in its infancy** - we would welcome both contributions
and comments, feel free to start a disucssion in the Issues tab.

Design
======

The continuity of the radio stream is up to Liquidsoap ;
in other words you have to write yourself the Liquidsoap script that will fit your radio.
We provide a few extracts to demonstrate the integration with Showergel.

Showergel is meant for community and benevolent radios.
Therefore we'll keep it small and simple:

* Showergel is intended to run on the same machine as Liquidsoap.
* It relies on Python3's SimpleHTTPRequestHandler_ because it's enough
  to provide an interface for a single stream,
  and it allows us to keep everything in a single process.
* Showergel's data is stored in SQLite_ because a database backing a radio stream
  usually weights a few dozen megabytes.
* Scheduling is delegated to APScheduler_ ... who also needs SQLAlchemy_ to
  access SQLite, so we use SQLAlchemy too.
* Showergel will not hold your music and shows collection.
  For that matter we suggest Beets_,
  you can find examples of its integration with Liquidsoap in
  `Liquidsoap documentation <https://www.liquidsoap.info/doc-dev/beets.html>`_.

Showergel have only been tested under Linux.

License: GPL3_.

Develop
=======

Depencencies, installation and packing is done by Poetry_.
Once Poetry is installed,
create a Python3 environment,
activate it, and run ``poetry install`` from the root folder.

Showergel is a light program made to run permanently along your Liqudidsoap instance.
It communicates with Liqudidsoap via its telnet server,
and with the outside world via HTTP.
Configure it by editing ``daemon.ini``,
then set up the DB with ``showergel_install daemon.ini``.
Finally run ``showergel daemon.ini``.


Custom authentication for ``input.harbor``
==========================================

*this will be moved to an HTTP endpoint*

``showergel/harbor_auth.py`` is an independant script
that can back a custom authentication function for ``input.harbor``,
where each user has her own password.
See the documentation in the script's docstring.


.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL3: https://www.gnu.org/licenses/gpl-3.0.html
.. _Poetry: https://python-poetry.org/
.. _APScheduler: https://apscheduler.readthedocs.io/en/stable/
.. _SQLite: https://sqlite.org/
.. _Beets: http://beets.io
.. _SimpleHTTPRequestHandler: https://docs.python.org/3/library/http.server.html#http.server.SimpleHTTPRequestHandler
.. _SQLAlchemy: https://www.sqlalchemy.org/
