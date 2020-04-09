Application
===========


liteblue is a tornado Application and we subclass tornado.web.Application
to intialize our server. The start is a Config class:

.. autoclass:: liteblue.config.Config
    :members: name, port


This is passed to:

.. autoclass:: liteblue.server.Application
    :members:
