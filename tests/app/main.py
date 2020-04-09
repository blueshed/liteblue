"""
    tornado ws rpc server
"""
import logging
import os
from pkg_resources import resource_filename
from liteblue.server import Application
from liteblue.connection import ConnectionMgr
from liteblue import config

LOGGER = logging.getLogger(__name__)


class Config(config.Config):
    """ Access to configuration """

    name = "test-app"
    tornado_debug = True
    static_path = resource_filename("liteblue.apps", "static")
    procedures = "tests.app.procedures"
    alembic_script_location = "tests/alembic"
    db_url = os.getenv("DB_URL", "sqlite:///tests/test.db")
    connection_kwargs = config.Config.SQLITE_CONNECT_ARGS


class Prod(Config):
    """ mysql and redis config """

    db_url = "mysql+pymysql://root:secret@localhost:3309/simple"
    connection_kwargs = Config.MYSQL_CONNECT_ARGS
    connection_kwargs["echo"] = True
    redis_url = "redis://localhost:6381"


def make_app(cfg):
    ConnectionMgr.connection("default", cfg.db_url, **cfg.connection_kwargs)
    return Application(cfg)


def main():  # pragma: no cover
    """ run the application """
    make_app(Config).run()
