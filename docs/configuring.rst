.. _configuring:

Configuring Showergel
=====================

A configuration file is needed to start Showergel.
It tells the program what to do,
where data should be written,
how to contact Liquidsoap, etc.
Showergel's installer creates a minimal configuration,
(including comments if you're hurried to tweak it)
but you may need more or hesitate:
this section will tell you all configuration details and their implications, if any.

What's a ``.toml`` configuration file
-------------------------------------

Showergel uses the TOML_ format.
If you have never encountered it, let's start by describing *how* this configuration is written.
It is a text file, encoded in UTF-8,
that you can edit with the same program as your Liquidsoap script
(Notepad, gedit, vim, Eclipse, etc.).

Configuration properties have a *key* (usually a word)
and a *value* (a character string, a list, number, ...).
Properties are grouped by sections, like ``[listen]`` or ``[db.sqlalchemy]``.

Do not mix properties between sections:
usually, the program will look for a property below one perticular section.
*Comments* are notes that will be ignored by the program: they start with a ``#``.

A TOML file looks like this:

.. code-block:: toml

    [section]
    property = "value"
    somelist = ["foo", "bar", "baz"]
    secret = 9876

    [another_section]
    # this line starts with a sharp : programs will ignore it
    # you can use comments to note why a value is defined
    # or to put aside old configuration values
    debug = true  # comments can be at end of lines too

Showergel's installer creates a basic TOML file you should start with.
This page's sections match sections in Showergel's config file.

``[db.sqlalchemy]``
-------------------

This section should at least include a path to the instance's database file:

.. code-block:: toml

    url = "sqlite:////home/me/path/to/showergel.db"

Yes, that's four ``/``.
Use only 3 if you prefer a relative path (relative to Showergel's working directory),
for example ``sqlite:///showergel.db``.

If you do not want to write a file, just use ``sqlite:///:memory:``.
However with that setting Showergel will always forget its data when restarting.
This will disrupt metadata logging and users authentication,
but can be enough for a short test.
It is supported for unit testing and the online demo.

If you already have a DB server at hand,
you can use it for Showergel too.
You will have to install the DBAPI package youself,
and refer to SQLAlchemy's documentation for the URL format -
see pages about
`PostGreSQL <https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg2>`_
or `MySQL <https://docs.sqlalchemy.org/en/14/dialects/mysql.html#dialect-mysql>`_.

You may display DB requests in Showergel's log by setting the property ``echo = true``.
This can be useful when debugging.


``[interface]``
---------------

You may change the name displayed in the interface's left bar:

.. code-block:: toml

    name = "Showergel Radio 98.7 FM"


.. _configuration_server:

``[listen]``
------------

This defines Showergel's address for your browser and liquidsoap.
For example:

.. code-block:: toml

    address = "localhost"
    port = 2345

Using these (default) values,
Showergel's interface will be available at the URL http://localhost:2345/.
If you are running multiple instances of Showergel on the same machine,
be careful to set a different ``port`` for each one.

For some features (user authentication, metadata logging),
Showergel's URL must be set in your Liquidsoap script too.
See :ref:`liquidsoap`.

.. warning::
    The ``address`` property may be an IP address.
    If you change the address, ensure it is only accessible on a private network.

To have a more detailed server log you can add ``debug = true``.


.. _configuration_liquidsoap:

``[liquidsoap]``
----------------

This section defines how Showgel can contact Liquidsoap:

.. code-block:: toml

    method = "telnet"
    host = "localhost"
    port = 1234

This should match Liquidsoap's telnet parameters - see :ref:`liquidsoap`.

Other values can be set as ``method``:
 * ``none`` if you don't want to enable Showergel's "current track" display.
 * ``demo`` will simulate a Liquidsoap connection.
   In that case ``host`` and ``port`` are ignored.
   This is used by Showergel's online demo.
 * anything else, or if the parameter is missing, will simulate a Liquidsoap
   connection by generating different data each time it's called.
   This should only be used for Showergel's unit tests.

``[metadata_log]``
------------------

This section configures how Showergel stores tracks' metadata.
It may contain ``extra_fields``: a list of metadata fields that should be stored, when available.

.. code-block:: toml

    [metadata_log]
    extra_fields = [
        "genre",
        "language",
        "year",
        "track*",
    ]

A ``*`` in the field name represents any characters or nothing.
In the example above, ``track*`` will match ``track``,
but also ``track_number`` or ``tracktotal``.
Field names are stored as they are, so Showergel will store ``track_number`` or ``tracktotal``.

Logging configuration
---------------------

This follows Python's `configuration dictionary schema for logging
<https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema>`_.

.. _TOML: https://toml.io
