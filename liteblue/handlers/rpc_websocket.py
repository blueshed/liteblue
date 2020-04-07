# pylint: disable=W0201, W0221, W0223
"""
    A json rpc 2.0
"""
import uuid
from tornado.web import HTTPError
from tornado.websocket import WebSocketHandler as Ws
from .json_utils import dumps, loads
from .json_rpc_mixin import JsonRpcMixin as RpcMix
from .broadcast_mixin import BroadcastMixin as BcMix
from .user_mixin import UserMixin as UMix


class RpcWebsocket(UMix, BcMix, RpcMix, Ws):
    """ implementation """

    def initialize(self, procedures):
        """ what do we make available remotely """
        self.procedures = procedures
        self._id = str(uuid.uuid4())

    def open(self, *args, **kwargs):
        """ websocket open - register user """
        if self.current_user is None and self.settings.get("login_url"):
            raise HTTPError(403)
        self.init_broadcast()

    async def on_message(self, data):
        """ handle the action """
        content = loads(data)
        result = await self.handle_content(content)
        if result:
            self.write_message(dumps(result))

    def on_close(self):
        """ unregister us """
        self.end_broadcast()
