"""
    Proxy to procedures

    ...because it walks like a duck....

    should you wish to run locally::

        async with Moo(Config) as cow:
            result = await cow.add(2, 2)
            assert result == 4

"""
import logging
from importlib import import_module
from tornado.ioloop import IOLoop
from . import context
from .config import Config

LOGGER = logging.getLogger(__name__)


class Moo:
    """ we want a proxy """

    def __init__(self, config: Config, io_loop: IOLoop = None, user=None):
        self._rpc_ = import_module(config.procedures)
        self._loop_ = io_loop if io_loop else IOLoop.current()
        context.LOOP = self._loop_
        self._user_ = user

    async def __aenter__(self):
        """ act as an async context manager """
        return self

    async def __aexit__(self, type_, value, traceback):
        """ act as an async context manager """

    def __getattribute__(self, name):
        """ public attributes are proxies to procedures """
        LOGGER.debug("attribute %s", name)
        if name[0] == "_":
            return super().__getattribute__(name)
        rpc = self._rpc_
        if name in rpc.__all__:
            proc = getattr(rpc, name)
            assert proc, f"no such procedure {name}"

            def _wrapped_(*args, **kwargs):
                LOGGER.info("calling %s(*%r, **%r)", name, args, kwargs)
                return context.perform(self._user_, proc, *args, **kwargs)

            return _wrapped_
        raise AttributeError(f"no such procedure: {name}")
