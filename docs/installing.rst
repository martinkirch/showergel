Installing Showergel
====================

Installing Showergel requires
 * a Linux box relying on systemd (ie. a recent mainstream distribution),
   with only user access,
 * Python, at least v3.7,
 * check pip_ is available, by calling ``pip3 --version`` (or ``pip --version``)
 * a running Liquidsoap radio - `version 1.4.4 <https://www.liquidsoap.info/doc-1.4.4/install.html>`_
   is Showergel's best friend.

.. note::
  
  We assume you already know the basics of Liquidsoap and its script language.
  If you have never played with only Liquidsoap, we advise you read at least
  `its quick start guide <https://www.liquidsoap.info/doc-1.4.4/quick_start.html>`_.
  Then you might jump to :ref:`quickstart`.

Install Showergel by running ``pip3 install showergel`` (maybe replace ``pip3`` by ``pip``).

Then you'll need to set-up your first instance.
Before that, let's explain briefly what it means.

What's a Showergel instance ?
-----------------------------

Technically, it is an instance of the ``showergel`` program.
It's an HTTP server:
it is able to serve an interface you can open in your browser,
and to answer queries called from your Liquidsoap script.

Functionally, an instance is the companion of *one* Liquidsoap stream.
The two programs will communicate with each other to produce and follow this stream.
An instance relies on some configuration (a ``.toml`` file) and a database (an SQLite file).
It can be installed as a system service,
named after information you provide at set-up time.

If you are running multiple Liquidsoap streams on the same machine,
you'll have to set up one Showergel instance per stream.
In that case,

* each instance should have a different name
* each instance should run on a different port number

We advise you to put all instance's files (configuration, DB, logs)
in the same folder as the corresponding ``.liq`` file.
When running multiple Liquidsoaps, create a folder per instance.


Create an instance with the interactive installer
-------------------------------------------------

Run the interactive installer by calling ``showergel_install``.
It will explain on the terminal what is happening and what to do from here.
If you stick to defaults, the instance's basename will be ``showergel``,
so the installer will:

* create a database (``showergel.db``)
  and a configuration file (``showergel.toml``) in the current directory,
* create a systemd user service called ``showergel`` ;
  in other words you can ``systemctl --user status|start|stop|restart showergel``.
* enable the service and systemd's lingering_ so Showergel will start automatically at boot time.

The installer allows you to create another systemd user service, for your Liquidsoap script.
This is recommended, because then systemd will automatically launch both Showergel and Liquidsoap,
and restart them when a crash happens.
If you do so, the installer creates two systemd services with the same basename:
for example, ``radio_gel`` (Showergel service associated to ``radio``)
and ``radio_soap`` (wrapper for the Liquidsoap script you provided for ``radio``).

If you choose to not create a service, you will have to (re)start Showergel
manually by calling ``showergel showergel.toml``.

Before exiting, the installer gives a recap of its actions.

.. note::
  Please pay attention to the installer's recap:
  it lists how to run/stop Showergel and gives pointers to important files.
  Read it twice and copy this information safely.

Unless you configured another port, Showergel will be available at http://localhost:2345/.
Showergel's and Liquidsoap's configurations are coupled.
In perticular, they should define which port/URL should be used to contact each other:
see :ref:`configuring` and :ref:`liquidsoap`.

If you installed Showergel as a system service,
don't forget to restart showergel's service after editing its configuration file.
If you installed your Liquidsoap script as a system service,
restart this service after editing the script - and after running ``liquidsoap --check my_script.liq`` !
In both cases, log files are in the same folder as instance's other files.


Install for back-end development
--------------------------------

Depencencies, installation and packing is done by Poetry_.
Once Poetry is installed,
create a Python3 environment,
activate it, and run ``poetry install`` from a clone of
`Showergel's repository <https://github.com/martinkirch/showergel>`_.

When developping, your Liquidsoap script and Showergel should be launched manually.
Run ``showergel_install --dev`` to create an empty database (``showergel.db``)
and a basic configuration file (``showergel.toml``)
in the current folder.
Read (and edit, maybe) ``showergel.toml``,
launch Liqudisoap, then run ``showergel showergel.toml``.
You'll likely want to enable the detailed log by setting ``level=DEBUG``
in the ``logger_root`` section of the toml file.

Test with ``pytest``. See also :ref:`releasing`.

Install for front-end development
---------------------------------

The front-end is written in JavaScript packed with Yarn_,
with VueJS_'s `single-file components <https://v3.vuejs.org/guide/single-file-component.html>`_.
We use the Bulma_ CSS Framework.

To modify the front-end, you must beforehand install Yarn and Vue_CLI_,
then run ``yarn install`` from the repository root.
Start the live-building server with ``yarn serve``.
If you don't have time to install the whole back-end,
you can call the demo app by creating a ``front/.env`` file that contains:

.. code-block::

    VUE_APP_BACKEND_URL=https://arcane-retreat-54560.herokuapp.com

Similarly, a fully-working HTML/JS/CSS build is included in this repository,
so one doesn't have to install ``yarn`` and Vue while working on the back-end.
Those files are generated by ``yarn build``.

.. note::
  
  Please do **not** commit modifications in the ``/showergel/www/`` folder.
  In order to avoid complex and useless conflicts, commits concerning this folder
  should only happen on the ``main`` branch.


Deploy to Heroku in demo mode
-----------------------------

In demo mode, the application starts by putting fake data in the database.
It's enabled by putting ``demo = True`` in the configuration file's ``[listen]`` section.

Source repository includes such a configuration,
so you can create and push the app right after cloning:

.. code-block:: bash

    heroku create --region eu
    git push heroku main
    heroku logs --tail

We might need to update ``requirements.txt`` from time to time:

.. code-block:: bash

    poetry export --dev --without-hashes -f requirements.txt --output requirements.txt

``--dev`` is here because ``requirements.txt`` is also used by ReadTheDocs
to compile the present documentation, which requires a Sphinx extension.


.. _Poetry: https://python-poetry.org/
.. _lingering: https://www.freedesktop.org/software/systemd/man/loginctl.html
.. _Yarn: https://yarnpkg.com/
.. _VueJS: https://vuejs.org/
.. _Bulma: https://bulma.io/
.. _Vue_CLI: https://cli.vuejs.org/
.. _pip: https://pip.pypa.io/en/stable/installing/
