# pylint: disable=W0201, W0223
"""
    A json rpc 2.0
"""
import logging
from tornado.web import RequestHandler, HTTPError
from .json_rpc_mixin import JsonRpcMixin as RpcMix
from .user_mixin import UserMixin as UMix
from . import json_utils

LOGGER = logging.getLogger(__name__)


class RpcHandler(UMix, RpcMix, RequestHandler):
    """ marshall json rpc 2.0 requests and respond """

    @property
    def procedures(self):
        """ what we make available """
        return self.settings["procedures"]

    async def post(self):
        """ We only handle the post method """
        if self.settings.get("login_url") and self.current_user is None:
            raise HTTPError(403)
        content = json_utils.loads(self.request.body)
        result = await self.handle_content(content)
        LOGGER.debug("result: %s", result)
        if result:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json_utils.dumps(result))
