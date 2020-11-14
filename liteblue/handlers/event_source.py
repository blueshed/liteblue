# pylint: disable=W0201, W0223
"""
    Broadcast function  without Websockets
"""
import logging
from tornado.web import RequestHandler, authenticated
from .broadcast_mixin import BroadcastMixin
from .user_mixin import UserMixin as UMix
from . import json_utils

LOGGER = logging.getLogger(__name__)


class EventSource(UMix, BroadcastMixin, RequestHandler):
    """
    Queue of messages to send to client
    """

    def initialize(self):
        """
        Set up response headers and prepare
        local queue and add self to clients
        """
        self.set_header("content-type", "text/event-stream")
        self.set_header("cache-control", "no-cache")
        self.init_broadcast()
        LOGGER.debug("init")

    @authenticated
    async def get(self):
        """ handle a connection """
        LOGGER.debug("get")
        await self.flush()
        self.init_broadcast()

    async def write_message(self, data):
        """ to look like a websocket for BroadcastMixin """
        self.write(f"data: {data}\n\n")
        await self.flush()
        LOGGER.debug("wrote %s", data)

    def ping(self, msg):
        """ handle keep alive """
        self.queue.put_nowait(json_utils.dumps({"action": "ping", "message": msg}))
