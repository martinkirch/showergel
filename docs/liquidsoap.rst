.. _liquidsoap:

Showergel integration in Liquidsoap scripts
===========================================

Most Showergel features require your Liquidsoap script to implement a link with Showergel.
This page presents these links, as seen from Liquidsoap.
**All examples below assume your Liquidsoap script starts with a variable defining Showergel's URL, as:**

.. code-block:: ocaml

    SHOWERGEL = "http://localhost:2345"


.. _quickstart:

Showergel's quickstart.liq
--------------------------

We showcase the complete Showergel integration in a "quick-start script" you can download
:download:`here <_static/quickstart.liq>`.
It is tested against Liquidsoap 1.4.4.
This ``.liq`` file defines typical radio sources and is heavily commented:
you can use it to start your first stream, or pick portions that would improve
your existing script (it also contain a few Liquidsoap tricks!).

.. warning::
    Showergel and Liquidsoap are **not** secured against malicious access.
    In the worst case, this could result in innapropriate control of your radio's program.
    Please isolate the machine running Showergel on both physical and network levels.

Sections below discuss implementation details on integrating each Showergel feature.


Display/skip current track
--------------------------

You just need to enable `Liquidsoap's telnet server <https://www.liquidsoap.info/doc-1.4.4/server.html>`_.
For example:

.. code-block:: ocaml

    set("server.telnet",true)
    set("server.telnet.bind_addr","127.0.0.1")
    set("server.telnet.port",1234)

``127.0.0.1`` is the IP address of ``localhost``.
The ``port`` value should match the one in Showergel's configuration's
:ref:`configuration_liquidsoap` section.
If you are running multiple instances of Liquidsoap on the same machine,
be careful to set a different ``port`` for each one.

.. warning::
    Do not use a public IP address as ``bind_addr``.
    This would open your Liquidsoap instance to the Internet,
    and someone might connect and mess up your programs.

.. _liq_metadata:

Logging metadata
----------------

You need to define a function that will post metadata to Showergel.

For Liquidsoap version 1.x,
you have to insert this function in your stream using the
`on_metadata <https://www.liquidsoap.info/doc-1.4.4/reference.html#on_metadata>`_
or
`on_track <https://www.liquidsoap.info/doc-1.4.4/reference.html#on_track>`_
operators, as follows:

.. code-block:: ocaml

    def post_to_showergel(m)
        response = http.post("#{SHOWERGEL}/metadata_log",
            headers=[("Content-Type", "application/json")],
            data=json_of(m))
        log(label="posted_to_showergel", string_of(response))
    end

    radio = on_track(post_to_showergel, source)

Once this is defined, be careful to use ``radio`` as your outputs' source (instead of ``source``).
Otherwise ``post_to_showergel`` will never be called and nothing will be logged.

For Liquidsoap version 2.x, you just have to call
`source.on_track <https://www.liquidsoap.info/doc-dev/reference.html#source.on_track>`_
or `source.on_metadata <https://www.liquidsoap.info/doc-dev/reference.html#source.on_track>`_
:

.. code-block:: ocaml

    def post_to_showergel(m)
        response = http.post("#{SHOWERGEL}/metadata_log",
            headers=[("Content-Type", "application/json")],
            data=json_of(m))
        log(label="posted_to_showergel", string_of(response))
    end

    source.on_track(radio, post_to_showergel)

The line that starts with ``log`` is optional,
it may help when debugging.

.. warning::
    Many Liquidsoap operators repeat previous track's metadata when switching
    from a source to a another.
    This concerns operators whose ``replay_metadata`` parameter defaults to ``true``.
    This often yields duplicate entries in the log,
    although Showergel does its best to ignore duplicates.

    In other words, if you get duplicates in the metadata log,
    you might avoid them by adding ``replay_metadata=false`` to your
    ``fallback``/``random``/``rotate``/``switch`` operators.
    Especially if they're track-insensitive.


.. _liq_login:

Authenticating users on harbor
------------------------------

Liquidsoap's `input.harbor <https://www.liquidsoap.info/doc-1.4.4/reference.html#input.harbor>`_
can require authentication by giving ``user`` and ``password`` parameters.
But this implies

* storing the clear password in your ``.liq`` script
* sharing those credentials
* restarting the Liquidsoap stream when you want to update those credentials

This is not enough secured and unconvenient.

Instead, you can rely on Showergel to hold the list of users and their (encrypted) passwords.
Then you will be able to add/edit crendentials from Showergel's web interface.
This method requires creating an authentication function (in your ``.liq``)
passed to ``intput.harbor``'s ``auth`` parameter (instead of ``user`` and ``password``).

For Liquidsoap version 1.x, this function can be written as:

.. code-block:: ocaml

    def auth_function(user, password) =
        let (status, _, _) = http.post("#{SHOWERGEL}/login",
            headers=[("Content-Type", "application/json")],
            data=json_of([("username", user), ("password", password)])
        )
        let (_, code, _) = status
        if code == 200 then
            log("Access granted to #{user}")
            true
        else
            log("Access denied to #{user}")
            false
        end
    end

    harbor = input.harbor(auth=auth_function, ...

For Liquidsoap version 2.x, this function can be written as:

.. code-block:: ocaml

    def auth_function(user, password) =
        response = http.post("#{SHOWERGEL}/login",
            headers=[("Content-Type", "application/json")],
            data=json_of([("username", user), ("password", password)])
        )
        if response.status_code == 200 then
            log("Access granted to #{user}")
            true
        else
            log("Access denied to #{user}")
            false
        end
    end

    harbor = input.harbor(auth=auth_function, ...
