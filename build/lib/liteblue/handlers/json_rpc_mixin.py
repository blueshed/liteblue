# pylint: disable=W0201
"""
    A json rpc 2.0
"""
import logging

LOGGER = logging.getLogger(__name__)


class NoAccess(Exception):
    """ called when you should not see this """


class JsonRpcException(Exception):
    """ Throw xception that capture message """

    def __init__(self, code, message):
        super().__init__(self, message)
        self.js_code = code
        self.js_message = message


class JsonRpcMixin:
    """ Common functions used by both ws and http """

    @classmethod
    def get_params(cls, content):
        """ split params into args and kwargs """
        if isinstance(content["params"], dict):
            return [], content["params"]
        if isinstance(content["params"], list):
            return content["params"], {}
        raise JsonRpcException(-32602, "Params neither list or dict")

    async def handle_content(self, content):  # noqa: 901
        """ Assumes a json 2.0 method conent """
        LOGGER.info(content)
        result = {"jsonrpc": "2.0"}
        try:
            if content.get("jsonrpc") != "2.0":
                raise JsonRpcException(-32600, "protocol not supported")
            ref = content.get("id", None)
            if ref:
                result["id"] = ref

            method = content.get("method")
            if method is None:
                raise JsonRpcException(-32600, "no method")
            if method[0] == "_":
                raise JsonRpcException(-32600, "method private")
            if method not in self.procedures.__all__:
                raise JsonRpcException(-32600, f"no such method: {method}")

            user = self.current_user
            args, kwargs = self.get_params(content)
            LOGGER.debug("%s %s %s %s", user, method, args, kwargs)

            result["result"] = await self.application.perform(
                user, method, *args, **kwargs
            )
            if ref is None:
                result = None  # its a notification

        except JsonRpcException as ex:
            LOGGER.exception(ex)
            result["error"] = {"code": ex.js_code, "message": ex.js_message}
        except Exception as ex:  # pylint: disable=W0703
            LOGGER.exception(ex)
            result["error"] = {"code": -32000, "message": str(ex)}
        LOGGER.debug(repr(result))
        return result
