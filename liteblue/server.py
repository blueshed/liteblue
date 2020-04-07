"""
    tornado ws rpc server
"""
import logging
from importlib import import_module
from tornado import web, ioloop
from liteblue import handlers
from liteblue import ConnectionMgr
from liteblue import authentication
from liteblue import context

LOGGER = logging.getLogger(__name__)


def make_app(cfg):
    """ used also by tests """
    procedures = import_module(cfg.procedures)
    settings = {k[8:]: getattr(cfg, k) for k in dir(cfg) if k.startswith("tornado_")}
    routes = [
        (
            r"/login",
            handlers.LoginHandler,
            {"login": authentication.login, "register": authentication.register,},
        ),
        (r"/logout", handlers.LogoutHandler),
        (r"/events", handlers.EventSource),
        (r"/rpc", handlers.RpcHandler, {"procedures": procedures}),
        (r"/ws", handlers.RpcWebsocket, {"procedures": procedures}),
        (
            r"/(.*)",
            handlers.AuthStaticFileHandler
            if settings.get("login_url")
            else web.StaticFileHandler,
            {"default_filename": "index.html", "path": cfg.static_path},
        ),
    ]
    return web.Application(routes, **settings)


def main(cfg):  # pragma: no cover
    """ run the application """
    ConnectionMgr.connection("default", cfg.db_url, **cfg.connection_kwargs)
    app = make_app(cfg)
    app.listen(cfg.port)
    context.Context.init(cfg)
    LOGGER.info("%s on port: %s", cfg.name, cfg.port)
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("shut down.")
