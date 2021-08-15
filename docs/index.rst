Welcome to Showergel's documentation!
=====================================

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel provides complementary features like playlist logging or occasional
scheduling, with a (minimalist) Web interface.
It is made to run on a Linux box (with systemd) dedicated to your radio stream.

.. note::

    With Showergel you still have to write/tune the Liquidsoap script that will fit your radio.
    That is, the set of sources
    (`playlist <https://www.liquidsoap.info/doc-dev/reference.html#playlist>`_,
    `input.harbor <https://www.liquidsoap.info/doc-dev/reference.html#input.harbor>`_,
    ...)
    and operators
    (`random <https://www.liquidsoap.info/doc-dev/reference.html#random>`_,
    `switch <https://www.liquidsoap.info/doc-dev/reference.html#switch>`_,
    `fallback <https://www.liquidsoap.info/doc-dev/reference.html#fallback>`_,
    ...)
    that fits your programs and schedule.
    This documentation only provides :ref:`quickstart`,
    covering Liquidsoap's basics and Showergel's integration.
    Please take some time to experiment with Liquidsoap alone before
    considering Showergel.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   design
   installing
   configuring
   liquidsoap
   rest
   releasing
   
Showergel is released under the GPL3_ license.
   
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Liquidsoap: https://www.liquidsoap.info/
.. _GPL3: https://www.gnu.org/licenses/gpl-3.0.html
   