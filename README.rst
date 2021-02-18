=========
Showergel
=========

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel provides complementary features like logging or occasional scheduling,
with a (minimalist) Web interface.
It is made to run on a Linux box (with systemd) dedicated to your radio stream.

**This is work in progress!** We'll welcome both contributions
and comments, feel free to start a disucssion in the Issues tab.

News
====

Right after the 0.1.0 release, 
Showergel has been presented at Liquidshop_1.0_, 
the very first Liquidsoap workshop !
You can watch the 15-minutes presentation on Youtube_,
slides are in the repository's ``doc`` folder.

Install
=======

Install the program by the running ``pip install showergel``.

Run the interactive installer by calling ``showergel_install``.
It will explain on the terminal what is happening and what to do from here.
If you stick to defaults, the installer will:

* create a database (``showergel.db``)
  and a configuration file (``showergel.ini``) in the current directory,
* create a systemd user service called ``showergel`` ;
  in other words you can ``systemctl --user status|start|stop|restart showergel``.
* enable the service and systemd's lingering_ so Showergel will start automatically at boot time.
* after installation Showergel will be available at http://localhost:2345/.

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

Test with ``pytest``.

A font-end is coming up for v 0.2.0, see front/README.md 

Design
======

Showergel is a light program made to run permanently along your Liqudidsoap instance.
It communicates with Liqudidsoap via its telnet server,
and with the outside world via HTTP.

We assume that most of the program time should be handled by your Liquidsoap script,
typically with the ``random`` operator over a music folder
or a ``switch`` scheduling regular pre-recorded shows.

In other words you still have to write yourself the Liquidsoap script that will fit your radio.
We only provides a few examples,
covering Liquidsoap's basics and Showgel's integration.

Showergel is meant for community and benevolent radios.
Therefore we'll keep it small and simple:

* Showergel is intended to run on the same machine as Liquidsoap.
* The REST/Web interface is served by the Bottle_ framework,
  because it's enough and allows keeping everything in a single process.
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


.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL3: https://www.gnu.org/licenses/gpl-3.0.html
.. _Poetry: https://python-poetry.org/
.. _APScheduler: https://apscheduler.readthedocs.io/en/stable/
.. _SQLite: https://sqlite.org/
.. _Beets: http://beets.io
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _lingering: https://www.freedesktop.org/software/systemd/man/loginctl.html
.. _Bottle: https://bottlepy.org/docs/dev/
.. _Liquidshop_1.0: http://www.liquidsoap.info/liquidshop/
.. _Youtube: https://www.youtube.com/watch?v=9U2xsAhz_dU
