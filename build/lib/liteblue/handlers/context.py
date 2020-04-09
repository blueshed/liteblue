""" context for procedure calls """
import contextvars
from .broadcast_mixin import BroadcastMixin

USER = contextvars.ContextVar("USER")


def current_user():
    """ returns the user(actor) for this procedure call """
    return USER.get(None)


def broadcast(data, user_ids=None):
    """ broadcast to WebSocket """
    BroadcastMixin.broadcast(data, user_ids)
