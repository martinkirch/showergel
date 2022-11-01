=========
Showergel
=========

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel provides complementary features like playlist logging or occasional
scheduling, with a (minimalist) Web interface.
It is made to run on a Linux box (with systemd) dedicated to your radio stream.

Documentation and
`installation instructions <https://showergel.readthedocs.io/en/latest/installing.html>`_
are hosted
on https://showergel.readthedocs.io/. 

**This is work in progress!** We'll welcome both contributions
and comments, feel free to start a disucssion in the Issues tab.

Showergel have only been tested under Linux.

License: GPL3_.

News
====

*1/11/2022:* Installer scripts are coming ! Right now it works on the latest Ubuntu, open a terminal and launch

.. code-block:: bash

    wget https://raw.githubusercontent.com/martinkirch/showergel/main/installers/showergel_quickstart.sh && chmod +x showergel_quickstart.sh && ./showergel_quickstart.sh

*17/08/2022:* We've just pusbluished a pre-release of Showergel version 0.3,
the first version compliant with Liquidsoap 2.x. Install it with `pip install --pre showergel`.

.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL3: https://www.gnu.org/licenses/gpl-3.0.html
