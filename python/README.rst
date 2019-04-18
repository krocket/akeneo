Akeneo API REST - Python Client
===============================

A Python wrapper for the Akeneo REST API. Easily interact with the Akeneo REST API using this library.


Installation
------------

.. code-block:: bash

    pip install akeneo


Getting started
---------------

Generate API credentials (Consumer Key & Consumer Secret) following this instructions https://api.akeneo.com/getting-started-admin.html.

Check out the Akeneo API endpoints and data that can be manipulated in https://api.akeneo.com/api-reference-index.html.


Basic setup
-----------

Basic setup for the Akeneo REST API:

.. code-block:: python

    from akeneo import AkeneoAPI

    akeneo = AkeneoAPI(
        url="AKENEO_INSTANCE_URL",
        client_id="YOUR_CLIENT_ID",
        secret="YOUR_SECRET",
        username="YOUR_USERNAME",
        password="YOUR_PASSWORD",
    )


Response
--------

All methods will directly return the JSON response from the API.


Changelog
---------

0.0.1
~~~~~

- Initial version: Every endpoint should be ok, except these ones for 'Media files'.
