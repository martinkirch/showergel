=======
Soapbox
=======

Although a single Liquidsoap_ script is able to create a radio stream,
some features must be implemented externally.
This project implements such features with a coherent set of Python scripts:
the following documentation also describes how they can be integrated in your own Liquidsoap script.
Those scripts are intended to run on the same machine as Liquidsoap,
and have only been tested under Linux.

License: GPL_.

Develop
=======

Depencencies, installation and packing is done by Poetry_.
Once Poetry is installed,
create a Python3 environment,
activate it, and run ``poetry install`` from the root folder.

Custom authentication for ``input.harbor``
==========================================

``soapbox/harbor_auth.py`` is an independant script
that can back a custom authentication function for ``input.harbor``,
where each user has her own password.
See the documentation in the script's docstring.

Soapbox Daemon [still in development]
=====================================

``soapbox_daemon`` is a light program made to run permanently along your Liqudidsoap instance.
It communicates with Liqudidsoap via its telnet server,
and with the outside world via HTTP (using a RESTful interface).

Set it up with ``soapbox_daemon_install daemon.ini``.


GUI [still in development]
==========================

Inspired from Savonet's Liguidsoap_, but using Python3, GTK3 (via PyGObject_) and Glade_.



.. _Liguidsoap: https://github.com/savonet/liquidsoap/tree/master/gui
.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL: https://www.gnu.org/licenses/gpl.html
.. _PyGObject: https://pygobject.readthedocs.io/en/latest/devguide/dev_environ.html
.. _Poetry: https://python-poetry.org
.. _Glade: https://glade.gnome.org/
