"""
    Proxy to procedures

    ...because it walks like a duck....

    should you wish to run locally::

        async with Moo('<procedures package name>') as cow:
            result = await cow.add(2, 2)
            assert result == 4

"""

import logging
from importlib import import_module
from tornado.ioloop import IOLoop
from liteblue import context

LOGGER = logging.getLogger(__name__)


class Moo:
    """ we want a proxy """

    def __init__(self, config: str, io_loop: IOLoop = None, user=None):
        self._rpc_ = import_module(config.procedures)
        self._loop_ = io_loop if io_loop else IOLoop.current()
        self._user_ = user

    async def _stop_(self):
        """ call this to shutdown the rpc """
        # self._exc_.shutdown()

    async def __aenter__(self):
        """ act as an async context manager """
        context.Context.init(io_loop=self._loop_)
        return self

    async def __aexit__(self, type_, value, traceback):
        """ act as an async context manager """
        await self._stop_()

    def __getattribute__(self, name):
        """ public attributes are proxies to procedures """
        LOGGER.debug("attribute %s", name)
        if name[0] == "_":
            return super().__getattribute__(name)
        if name in self._rpc_.__all__:
            proc = getattr(self._rpc_, name)
            assert proc

            def _wrapped_(*args, **kwargs):
                LOGGER.debug("calling %s(*%s, ***%s)", name, args, kwargs)
                return context.do_proc(self._user_, proc, *args, **kwargs)

            return _wrapped_
        raise AttributeError(f"no such procedure: {name}")
