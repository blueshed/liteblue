""" context for procedure calls """
import contextlib
import contextvars
import inspect
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop
from .broadcast_mixin import BroadcastMixin

LOGGER = logging.getLogger(__name__)

_USER_ = contextvars.ContextVar("_USER_")


def current_user():
    """ returns the user(actor) for this procedure call """
    return _USER_.get(None)


@contextlib.contextmanager
def _user_call_(user=None):
    """ With this we setup contextvars and reset """
    utoken = _USER_.set(user)
    try:
        yield
    finally:
        _USER_.reset(utoken)


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


class Context:
    """ tornado does not keep track of default io_loop """

    io_loop = None

    @classmethod
    def init(cls, config=None, io_loop=None):
        """ called to initialize _broadcast_ attribute """

        max_workers = config.max_workers if config else None
        cls.io_loop = io_loop if io_loop else IOLoop.current()
        cls.io_loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers))
        BroadcastMixin.init_broadcasts(
            topic_name=config.redis_topic if config else None,
            redis_url=config.redis_url if config else None,
            io_loop=cls.io_loop,
        )

    @classmethod
    async def do_proc(cls, user, proc, *args, **kwargs):
        """ runs a proc in threadpool or ioloop """

        todo = partial(proc, *args, **kwargs)

        if inspect.iscoroutinefunction(proc):
            LOGGER.debug("coroutine %s", todo)
            result = await _aperform_(user, todo)
        else:
            LOGGER.debug("thread %s", todo)
            result = await cls.io_loop.run_in_executor(None, _perform_, user, todo)
        return result


def do_proc(user, proc, *args, **kwargs):
    """ runs a proc in threadpool or ioloop """
    return Context.do_proc(user, proc, *args, **kwargs)
