===============
Soap Controller
===============

Connects to a running Liquidsoap_ instance to control its sources while it's playling.

Inspired from Savonet's Liguidsoap_, but using Python3, GTK3 (via PyGObject_) and Glade_.

License: GPL_.

Develop
=======

Because of ``python-systemd`` you should firstly install::

    sudo apt-get install libsystemd-dev gcc python3-dev pkg-config

(See https://github.com/systemd/python-systemd#to-build-from-source)

Depencencies, installation and packing is done by Poetry_.
Once Poetry is installed,
create a Python3 environment,
activate it, and run ``poetry install`` from the root folder.

This will install the main program : ``soap_controller``.

.. _Liguidsoap: https://github.com/savonet/liquidsoap/tree/master/gui
.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL: https://www.gnu.org/licenses/gpl.html
.. _PyGObject: https://pygobject.readthedocs.io/en/latest/devguide/dev_environ.html
.. _Poetry: https://python-poetry.org
.. _Glade: https://glade.gnome.org/
