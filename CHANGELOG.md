Changes and release history
===========================

0.1.x
=====

**0.1.0** is the initial release. It provides
 - an installer
 - an user table and a RESTful interface for user management
 - a metadata logger and its RESTful interface

Fix releases:
 - **0.1.1** fixes the DB path written by the installer
 - **0.1.2** enforces uniqueness on ``log.on_air``. Re-create your database,
    or run ``drop index ix_log_on_air; create unique index ix_log_on_air ON log (on_air);``
    in ``sqlite3 your.db``.
