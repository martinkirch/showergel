Showergel: a helper for Liquidsoap-based radios
===============================================

Showergel is made to live aside Liquidsoap_:
while a Liquidsoap script creates a radio stream,
Showergel provides complementary features like playlist logging or occasional
scheduling, with a Web interface.
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
    This documentation provides a :ref:`quickstart` script,
    covering Liquidsoap's basics and Showergel's integration.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   what
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
   