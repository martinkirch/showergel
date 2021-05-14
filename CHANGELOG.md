Changes and release history
===========================

0.2.x
=====

This is Showergel's second experimental release.

 - switch to TOML format for configuration file.
 - metadata configuration now expects a list of fields you'd like to store (it was an exclusion list in 0.1).
 - added a front-end.
 - added `interface.name` parameter
 - added a Liquidsoap connection . Must be configured in the `liquidsoap` section.

0.1.x
=====

**0.1.0** is the initial release. It provides
 - an installer
 - an user table and a RESTful interface for user management
 - a metadata logger and its RESTful interface

Fix releases:
 - **0.1.1** fixes the DB path written by the installer
 - **0.1.2** enforces uniqueness on ``log.on_air`` (avoids duplicates in log).
    Re-create your database,
    or run ``drop index ix_log_on_air; create unique index ix_log_on_air ON log (on_air);``
    in ``sqlite3 your.db``.
 - **0.1.3** add the possibility to set the binding port via an environment variable
