"""
    tornado ws rpc server
"""
import logging
import os
from liteblue import config
from liteblue import Application, ConnectionMgr

LOGGER = logging.getLogger(__name__)


class Config(config.Config):
    """ Access to configuration """

    name = "test-app"
    static_path = "tests/app/static"
    procedures = "tests.app.procedures"
    alembic_script_location = "tests/alembic"
    db_url = os.getenv("DB_URL", "sqlite:///tests/test.db")
    connection_kwargs = config.Config.SQLITE_CONNECT_ARGS


class Prod(Config):
    """ mysql and redis config """

    db_url = "mysql+pymysql://root:secret@localhost:3309/simple"
    connection_kwargs = Config.MYSQL_CONNECT_ARGS
    redis_url = "redis://localhost:6381"


def make_app(cfg):
    ConnectionMgr.connection("default", cfg.db_url, **cfg.connection_kwargs)
    return Application(cfg)


def main():  # pragma: no cover
    """ run the application """
    make_app(Config).run()
