"""
    tornado ws rpc server
"""
import logging
from importlib import import_module
from concurrent.futures import ThreadPoolExecutor
from tornado import web, ioloop
from . import handlers
from . import authentication
from .config import Config
from .worker import Channel

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
                        "page": getattr(cfg, "login_page", "login.html"),
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
        super().__init__(routes, procedures=procedures, app_name=cfg.name, **settings)
        self._cfg_ = cfg
        self._loop_ = io_loop if io_loop else ioloop.IOLoop.current()
        self._loop_.set_default_executor(
            ThreadPoolExecutor(max_workers=cfg.max_workers)
        )
        handlers.context.LOOP = self._loop_
        handlers.BroadcastMixin.init_broadcasts(
            self._loop_, cfg.redis_topic, cfg.redis_url
        )
        if self._cfg_.redis_workers:
            self.channel = Channel(cfg.redis_url, cfg.redis_queue)

    async def tidy_up(self):
        """ a nasty little method to clean up an io_loop for testing """
        if self._cfg_.redis_workers:
            await self.channel.tidy_up()
        await handlers.BroadcastMixin.tidy_up()

    async def perform(self, user, proc, *args, **kwargs):
        """ runs a proc in threadpool or ioloop """
        if self._cfg_.redis_workers:
            return await self.channel.perform(user, proc, *args, **kwargs)
        proc = getattr(self.settings["procedures"], proc)
        return await handlers.context.perform(user, proc, *args, **kwargs)

    def run(self):  # pragma: no cover
        """ run the application """
        self.listen(self._cfg_.port)
        if self._cfg_.tornado_debug:
            LOGGER.info("running in debug mode")
        LOGGER.info("%s on port: %s", self._cfg_.name, self._cfg_.port)
        try:
            self._loop_.start()
        except KeyboardInterrupt:
            logging.info("shut down.")
