=========
Showergel
=========

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel provides complementary features like playlist logging or occasional
scheduling, with a (minimalist) Web interface.
It is made to run on a Linux box (with systemd) dedicated to your radio stream.

**This is work in progress!** We'll welcome both contributions and comments,
feel free to write in the Issues or Discussions tabs.

License: GPL3_.

Take a look
-----------

If you'd like to see what it looks like,
check out our `demo installation <https://showergel.fly.dev>`_.
It is only the visible part of Showergel,
running on fake data.
You can also use it as a stub back-end
`when developping that interface <https://showergel.readthedocs.io/en/latest/installing.html#install-for-front-end-development>`_.


Quick install
-------------

Our automated script can install Liquidsoap and Showergel on an Ubuntu or Debian machine::

    wget https://raw.githubusercontent.com/martinkirch/showergel/main/installers/showergel_quickstart.sh && chmod +x showergel_quickstart.sh && ./showergel_quickstart.sh

The script will need to run `sudo`.
It will start the radio, you should hear it as soon as you put sound files in the `~/Music` folder.
It will also register the radio as a system service, so the radio and its interface will start when the machine reboots, too.

This script installs our "quickstart" LiquidSoap script.
After a first try we advise you to have a closer look to Showergel's documentation on https://showergel.readthedocs.io/. 


.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL3: https://www.gnu.org/licenses/gpl-3.0.html
