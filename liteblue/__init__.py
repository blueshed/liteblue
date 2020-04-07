""" rpc webserver """
from .connection import ConnectionMgr
from .handlers import BroadcastMixin, context
from .handlers.context import current_user
from .describe import describe, describe_sql
from .handlers import json_utils

VERSION = "0.0.1"


def broadcast(data, user_ids=None):
    """ broadcast to WebSocket """
    BroadcastMixin.broadcast(data, user_ids)
