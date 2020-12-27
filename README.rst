=========
Showergel
=========

While a Liquidsoap_ script creates a radio stream,
Showergel provides complementary features like metadata logging or occasional scheduling,
with a (minimalist, localhost-oriented) Web interface.
It can install itself (and your ``.liq``) as a systemd service.

It is meant to remain small and simple (a Python package using a SQLite DB),
for community/benevolent radios.
Showergel runs on a Linux box (with systemd) dedicated to your radio stream.

**This is a work in progress.**
Contributions and comments will be welcomed in the Issues tab.

License: GPL3_.


Install
=======

You'll need Python's pip ; run ``pip install showergel``.

Start the interactive installer by calling ``showergel_install``.
It will explain on the terminal what is happening and what to do from here.

If you stick to defaults, the installer will:

* create a database (``showergel.db``)
  and a configuration file (``showergel.ini``) in the current directory,
* create a systemd user service called ``showergel`` ;
  in other words you can ``systemctl --user status|start|stop|restart showergel``.
* enable the service and systemd's lingering_ so Showergel will start automatically at boot time.
* after installation Showergel will be available at http://localhost:1234/.

The installer's questions allow you to:

* change the name of the systemd service and the DB/configuration files' names.
  This is useful if you want to run multiple instances of showergel because you're
  broadcasting multiple programs from the same machine.
  For example, responding ``radio`` will create ``radio.db``, ``radio.ini`` and a ``radio`` service.
* skip the service creation, if you prefer to launch Showergel yourself.
* create another systemd user service for your Liquidsoap script,
  so systemd will automatically launch everything (this is recommanded).
  Note that in that case, the installer creates two systemd services with the
  same basename: for example,
  ``radio_gel`` (showergel service associated to ``radio``)
  and ``radio_soap`` (the Liquidsoap script you provided for ``radio``).


Configure
=========

See comments in the ``.ini`` file created by the installer.


Design principles: simplicity and modularity
============================================

Showergel is meant to provide additional blocks to your Liquidsoap instance,
like metadata logging or occasional scheduling.

*Occasional scheduling* means we assume that most of the program time is handled by your Liquidsoap script alone,
typically with the ``random`` operator over a music folder
or a ``switch`` scheduling regular pre-recorded shows.
In other words you still have to write yourself the Liquidsoap script that will fit your radio.
We only provides a few examples,
covering Liquidsoap's basics and Showgel's integration.

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

Develop
=======

Depencencies, installation and packing is done by Poetry_.
Once Poetry is installed,
create a Python3 environment,
activate it, and run ``poetry install`` from a clone of this repository.

When developping, your Liquidsoap script and Showergel should be launched manually.
Run ``showergel_install --dev`` to create an empty database (``showergel.db``)
and a basic configuration file (``showergel.ini``)
in the current folder.
Read (and edit, maybe) ``showergel.ini``,
launch Liqudisoap, then run ``showergel showergel.ini``.
You'll likely want to enable the detailed log by setting ``level=DEBUG``
in the ``logger_root`` section of the ini file.

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
.. _lingering: https://www.freedesktop.org/software/systemd/man/loginctl.html
