""" context for procedure calls """
import contextvars
import contextlib
import inspect
import logging
from functools import partial
from .broadcast_mixin import BroadcastMixin

LOGGER = logging.getLogger(__name__)

USER = contextvars.ContextVar("USER")

LOOP = None


def current_user():
    """ returns the user(actor) for this procedure call """
    return USER.get(None)


def broadcast(data, user_ids=None):
    """ broadcast to WebSocket """
    BroadcastMixin.broadcast(data, user_ids)


@contextlib.contextmanager
def _user_call_(user=None):
    """ With this we setup contextvars and reset """
    utoken = USER.set(user)
    try:
        yield
    finally:
        USER.reset(utoken)


class Performer:  # pylint: disable=R0903
    """ tidy namespace """

    @classmethod
    def _perform_(cls, user, func):
        """ perform a function with user in context """
        with _user_call_(user):
            return func()

    @classmethod
    async def _aperform_(cls, user, func):
        """ perform an async function with user in context """
        with _user_call_(user):
            return await func()

    @classmethod
    def perform(cls, user, proc, *args, **kwargs):
        """ perform in LOOP.executor or await """
        todo = partial(proc, *args, **kwargs)
        LOGGER.info("calling: %s", todo)

        if inspect.iscoroutinefunction(proc):
            result = cls._aperform_(user, todo)
        else:
            result = LOOP.run_in_executor(None, cls._perform_, user, todo)
        return result


def perform(_user_, proc, *args, **kwargs):
    """ perform a sync or async function """
    return Performer.perform(_user_, proc, *args, **kwargs)
