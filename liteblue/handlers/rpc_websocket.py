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
    """ Websocket Rpc Class """

    @property
    def procedures(self):
        """ what we make available """
        return self.settings["procedures"]

    def open(self, *args, **kwargs):
        """ websocket open - register user """
        self._id = str(uuid.uuid4())
        if self.current_user is None and self.settings.get("login_url"):
            raise HTTPError(403)
        self.init_broadcast()

    async def on_message(self, data):  # pylint: disable=W0236
        """ handle the action """
        content = loads(data)
        result = await self.handle_content(content)
        if result:
            self.write_message(dumps(result))

    def on_close(self):
        """ unregister user """
        self.end_broadcast()
