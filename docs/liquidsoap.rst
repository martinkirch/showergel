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
It is tested against Liquidsoap 2.0.x.
This ``.liq`` file defines typical radio sources and is heavily commented:
you can use it to start your first stream, or pick portions that would improve
your existing script (it also contain a few Liquidsoap tricks!).

.. warning::
    Showergel and Liquidsoap are **not** secured against malicious access.
    In the worst case, this could result in innapropriate control of your radio's program.
    Please isolate the machine running Showergel on both physical and network levels.

Sections below discuss implementation details on integrating each Showergel feature.

.. _liq_current:

Display/skip current track
--------------------------

You need to enable `Liquidsoap's telnet server <https://www.liquidsoap.info/doc-2.0.0/server.html>`_.
For example:

.. code-block:: ocaml

    settings.server.telnet.set(true)
    settings.server.telnet.bind_addr.set("127.0.0.1")
    settings.server.telnet.port.set(1234)

``127.0.0.1`` is the IP address of ``localhost``.
The ``port`` value should match the one in Showergel's configuration's
:ref:`configuration_liquidsoap` section.
If you are running multiple instances of Liquidsoap on the same machine,
be careful to set a different ``port`` for each one.

.. warning::
    Do not use a public IP address as ``bind_addr``.
    This would open your Liquidsoap instance to the Internet,
    and someone might connect and mess up your programs.

**If your script has multiple outputs**, ensure the main one has an identifier
by setting its ``id="identifier"`` parameter.
This identifier should be copied as ``output`` in the :ref:`configuration_liquidsoap` section.

.. _liq_metadata:

Logging metadata
----------------

You need to define a function that will post metadata to Showergel:

.. code-block:: ocaml

    def post_to_showergel(md)
        response = http.post("#{SHOWERGEL}/metadata_log",
            headers=[("Content-Type", "application/json; charset=UTF-8")],
            data=metadata.json.stringify(metadata.cover.remove(md))
        )
        if response.status_code != 200
        then
            log(label="Warning", "Error while posting metadata to Showergel: #{response} #{response.status_code} #{response.status_message}")
        end
    end

    radio.on_metadata(fun(m) -> thread.run(fast=false, {post_to_showergel(m)}))

We advise to plug the function with
`source.on_metadata <https://www.liquidsoap.info/doc-dev/reference.html#source.on_track>`_,
but `source.on_track <https://www.liquidsoap.info/doc-dev/reference.html#source.on_track>`_
may work too.

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

Liquidsoap's `input.harbor <https://www.liquidsoap.info/doc-2.0.0/reference.html#input.harbor>`_
can require authentication by giving ``user`` and ``password`` parameters.
But this implies

* storing the clear password in your ``.liq`` script
* sharing those credentials
* restarting the Liquidsoap stream when you want to update those credentials

This is unconvenient and not enough secured.

Instead, you can rely on Showergel to hold the list of users and their passwords - encrypted.
Then you will be able to add/edit crendentials from Showergel's web interface.
This method requires creating an authentication function (in your ``.liq``)
passed to ``intput.harbor``'s ``auth`` parameter (instead of ``user`` and ``password``).

This function can be written as:

.. code-block:: ocaml

    def auth_function(login) =
        response = http.post("#{SHOWERGEL}/login",
            headers=[("Content-Type", "application/json")],
            data=json.stringify(login)
        )
        if response.status_code == 200 then
            log("Access granted to #{login.user}")
            true
        else
            log("Access denied to #{login.user}")
            false
        end
    end

    harbor = input.harbor(auth=auth_function, ...
