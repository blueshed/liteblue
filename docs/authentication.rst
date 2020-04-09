Authentication
==============

You can run liteblue without authentication by settings the 
`tornado_login_url` to None in your config.Config. Otherwise
all the tornado setup is as expected: a `tornado_cookie_name` and 
a `tornado_cookie_secret`::

    class Config:
        """ sample config """
        ...
        tornado_debug = True
        tornado_cookie_name = f"{name}-user"
        tornado_cookie_secret = f"it was dark and stormy night for {name}"
        tornado_login_url = "/login"
        ....

`tornado_debug` controls the autoreloading of the app if source is changed.

These classes are implementations of authentication in tornado. They use
sqlalchemy and are configurable. You can write your own login and register
functions and pass them into the initialize of the LoginHandler.


.. automodule:: liteblue.authentication
   :members:

.. autoclass:: liteblue.handlers.login_handler.LoginHandler
    :members:

.. autoclass:: liteblue.handlers.login_handler.LogoutHandler
    :members:

.. autoclass:: liteblue.handlers.user_mixin.UserMixin
    :members: