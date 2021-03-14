What is Showergel ?
===================

Showergel is a light program made to run permanently along your Liqudidsoap instance.
It communicates with Liquidsoap via its telnet server and a RESTful interface,
and provides a web interface.

.. note::

    With Showergel you still have to write/tune the Liquidsoap script that will fit your radio.
    That is, the set of sources (
    `playlist <https://www.liquidsoap.info/doc-dev/reference.html#playlist>`_,
    `input.harbor <https://www.liquidsoap.info/doc-dev/reference.html#input.harbor>`_,
    ...)
    and operators (
    `random <https://www.liquidsoap.info/doc-dev/reference.html#random>`_,
    `switch <https://www.liquidsoap.info/doc-dev/reference.html#switch>`_,
    `fallback <https://www.liquidsoap.info/doc-dev/reference.html#fallback>`_,
    ...)
    that fits your programs and schedule.
    This documentation only provide a few examples,
    covering Liquidsoap's basics and Showgel's integration.

Showergel will handle Liquidsoap's missing features:

 * occasional scheduling,
 * tracks logging,
 * users authentication,
 * live interaction.

Design principles
-----------------

Showergel is meant for community and benevolent radios.
Therefore we'll keep it small and simple:

* Showergel is intended to run on the same machine as Liquidsoap.
* The REST/Web interface is served by the Bottle_ framework,
  because it's enough and allows keeping everything in a single process.
* Showergel's data is stored in SQLite_ because its architecture fits perfectly
  our use case (everything in a single, local file).
* Scheduling is delegated to APScheduler_, who also needs SQLAlchemy_ to
  access SQLite, so we use SQLAlchemy too.
* Showergel will not hold your music and shows collection.
  For that matter we suggest Beets_,
  you can find examples of its integration with Liquidsoap in
  `Liquidsoap documentation <https://www.liquidsoap.info/doc-dev/beets.html>`_.



.. _APScheduler: https://apscheduler.readthedocs.io/en/stable/
.. _SQLite: https://sqlite.org/
.. _Beets: http://beets.io
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _Bottle: https://bottlepy.org/docs/dev/
