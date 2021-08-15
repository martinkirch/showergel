.. _design:

Design considerations
=====================

Showergel is made for community and benevolent radios,
so it is meant to stay small and simple.
This is why we assume it runs on the same machine as Liquidsoap,
and make it as self-contained as possible.
Moreover, Showergel is made for Liquidsoap users.
That is, people programming their own radio scripts.
Because if you need a Web interface to schedule 100% of your programs without writing a
line of code, you already have good options as free software [#]_.

This page presents the modelling and components choices implied by these principles,
and their consequences.

What's inside Showergel - and what's not
----------------------------------------

The REST/Web interface is served by the Bottle_ framework,
because it's enough and allows keeping everything in a single process.
Bottle.py is bundled with Showergel as long as https://github.com/bottlepy/bottle/issues/1125 is not fixed.

Showergel's data is stored in SQLite_ because its more than enough and lets us
store everything in a single, local file.

Scheduling is delegated to APScheduler_, who also needs SQLAlchemy_ to
access SQLite, so we use SQLAlchemy too.

Showergel does not hold your music and shows collection.
For that matter we suggest Beets_.
You can find examples of its integration with Liquidsoap in
`Liquidsoap's documentation <https://www.liquidsoap.info/doc-dev/beets.html>`_.


Predicting Liquidsoap is hard
-----------------------------

Showergel is here to schedule what cannot be implemented with Liquidsoap's
scheduling functions, ie. *occasional* actions/programs
(Liquidsoap's `switch <https://www.liquidsoap.info/doc-dev/cookbook.html#scheduling>`_
is a better fit for regular programs).
And Showergel is meant to let you do anything allowed by Liquidsoap.
This implies that Showergel can't predict Liquidsoap's playlist.

This property of the Showergel-Liquidsoap couple 
might be the most surprising if you've ever worked with radio automation software:
*none of these two can predict what will be played at some point in time*.
Liquidsoap does not pre-compute its playlist, and neither does Showergel.

This boils down to the fact that, fundamentally,
Liquidsoap lets you write a stream generation function.
Predicting what will play out would require reverse-engineering users' scripts.
On its side, Showergel has a scheduler so it can predict what it will do, but that's not enough.
For example, even if you have scheduled
`remote_radio.start <https://www.liquidsoap.info/doc-dev/reference.html#input.http>`_
at some time, the remote stream might not be available right away:
what will play instead depends on what's in the Liquidsoap script.
As a user you're responsible not only for preparing fallback content for such case,
but also its conditions of appearance in the stream
(using `fallback <https://www.liquidsoap.info/doc-dev/reference.html#fallback>`_,
probably).

Most automation softwares relying on Liquidsoap try to hide this.
Indeed it is much simpler to let the user click on a weekly calendar.
But, in that setting, choosing an automation software forces you to abide by its scheduling logic.
Instead, we embrace Liquidsoap's DIY possibilities
and make all sources/outputs *you* created visible in Showergel.

Time
----

Showergel needs time zones to prevent a potential mismatch between the front and back ends:
Javascript's ``Date`` is always bound to a time zone.
Internally, time is represented on the UTC time zone
because SQLAlchemy's datetime for SQLite does not stores the time zone.
We use Arrow_ for data parsing and time zones conversions.

Showergel always expects and outputs times with time zone information (using the ISO 8601 format),
But Liquidsoap is not timezone-aware:
Liquidsoap endpoints or commands are converting time to the local time zone 
(guessed from the system's environment).


Events
------

Showergel proposes events to be set-up at milisecond precision
(although the GUI currently forces the milisecond term at zero).
Events are unrolled according to the schedule's order,
_never_ in parallel.
If an event might take a significant time (typically because it triggers a download)
note that it might delay following events.
This order is enforced because Showergel can't decide if events are dependent or not.


.. [#] among Liquidsoap-based solutions, we can cite LibreTime_, AzuraCast_,
         CrazyArms_, or AirTime_. See also Rivendell_.

.. _APScheduler: https://apscheduler.readthedocs.io/en/stable/
.. _SQLite: https://sqlite.org/
.. _Beets: http://beets.io
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _Bottle: https://bottlepy.org/docs/dev/
.. _AzuraCast: https://www.azuracast.com/
.. _LibreTime: https://libretime.org/
.. _AirTime: https://www.airtime.pro/
.. _CrazyArms: https://crazyarms.xyz/
.. _Rivendell: http://rivendellaudio.org/
.. _Arrow: https://arrow.readthedocs.io
