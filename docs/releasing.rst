.. _releasing:

Package and publish Showergel
=============================

Pre-publication check-list
--------------------------

 * Run ``poetry update``
 * Run ``pytest`` - all tests should pass
 * From the ``front`` folder, run ``yarn upgrade``.

If this is done right after a feature freeze,
the upcoming version should have a pre-release marker: ``-alpha.0``.
Run this pre-release for a few days in a realistic setup.

Build and check the documentation: ``cd docs; make html``.

Update version markers
----------------------

* ``version`` in ``pyproject.toml``
* ``version`` in ``front/package.json``
* ``release`` in ``docs/conf.py``

Package
-------

 * From the ``front`` folder, run ``yarn build``
 * ``poetry export --dev --without-hashes -f requirements.txt --output requirements.txt``
 * ``git commit,push,tag``
 * ``poetry build``
 * ``poetry publish``
