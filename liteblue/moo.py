"""
    Proxy to procedures

    ...because it walks like a duck....

    should you wish to run locally::

        async with Moo('<procedures package name>') as cow:
            result = await cow.add(2, 2)
            assert result == 4

"""
import inspect
import logging
import contextlib
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from tornado.ioloop import IOLoop
from liteblue.handlers import context

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def _user_call_(user=None):
    """ With this we setup contextvars and reset """
    utoken = context.USER.set(user)
    try:
        yield
    finally:
        context.USER.reset(utoken)


def _perform_(user, func):
    """ perform a function with user in context """
    LOGGER.debug("perform: %s", func)
    with _user_call_(user):
        return func()


async def _aperform_(user, func):
    """ perform an async function with user in context """
    LOGGER.debug("aperform: %s", func)
    with _user_call_(user):
        return await func()


class Moo:
    """ we want a proxy """

    def __init__(self, config: str, io_loop: IOLoop = None, user=None):
        self._rpc_ = import_module(config.procedures)
        self._loop_ = io_loop if io_loop else IOLoop.current()
        self._exc_ = ThreadPoolExecutor(max_workers=config.max_workers)
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
                LOGGER.info("calling %s(*%s, ***%s)", name, args, kwargs)
                todo = partial(proc, *args, **kwargs)

                if inspect.iscoroutinefunction(proc):
                    LOGGER.debug("coroutine %s", todo)
                    result = _aperform_(self._user_, todo)
                else:
                    LOGGER.debug("thread %s", todo)
                    result = self._loop_.run_in_executor(
                        self._exc_, _perform_, self._user_, todo
                    )
                return result

            return _wrapped_
        raise AttributeError(f"no such procedure: {name}")
