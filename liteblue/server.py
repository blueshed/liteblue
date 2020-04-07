"""
    tornado ws rpc server
"""
import logging
from importlib import import_module
from tornado import web, ioloop
from liteblue import handlers
from liteblue import authentication
from liteblue.moo import Moo
from liteblue.config import Config

LOGGER = logging.getLogger(__name__)


class Application(web.Application):
    """ subclass of tornado Application """

    def __init__(self, cfg: Config, routes: list = None, io_loop: ioloop.IOLoop = None):
        """ called to initialize _broadcast_ attribute """
        procedures = import_module(cfg.procedures)
        settings = {
            k[8:]: getattr(cfg, k) for k in dir(cfg) if k.startswith("tornado_")
        }
        routes = (
            routes
            if routes
            else [
                (
                    r"/login",
                    handlers.LoginHandler,
                    {
                        "login": authentication.login,
                        "register": authentication.register,
                    },
                ),
                (r"/logout", handlers.LogoutHandler),
                (r"/events", handlers.EventSource),
                (r"/rpc", handlers.RpcHandler),
                (r"/ws", handlers.RpcWebsocket),
                (
                    r"/(.*)",
                    handlers.AuthStaticFileHandler
                    if getattr(cfg, "tornado_login_url")
                    else web.StaticFileHandler,
                    {"default_filename": "index.html", "path": cfg.static_path},
                ),
            ]
        )
        super().__init__(routes, procedures=procedures, **settings)
        self._cfg_ = cfg
        self._loop_ = io_loop if io_loop else ioloop.IOLoop.current()
        self._moo_ = Moo(cfg, io_loop=self._loop_)
        handlers.BroadcastMixin.init_broadcasts(
            self._loop_, cfg.redis_topic, cfg.redis_url
        )

    async def tidy_up(self):
        """ a nasty little method to clean up an io_loop for testing """

        await handlers.BroadcastMixin.tidy_up()

    async def perform(self, user, proc, *args, **kwargs):
        """ runs a proc in threadpool or ioloop """

        self._moo_._user_ = user  # pylint: disable=W0212
        return await getattr(self._moo_, proc)(*args, **kwargs)

    def run(self):  # pragma: no cover
        """ run the application """
        self.listen(self._cfg_.port)
        LOGGER.info("%s on port: %s", self._cfg_.name, self._cfg_.port)
        try:
            self._loop_.start()
        except KeyboardInterrupt:
            logging.info("shut down.")
