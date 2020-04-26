import os
from pkg_resources import resource_filename
from liteblue import config


class _Config(config.Config):
    """ Access to configuration """

    name = "test-app"
    tornado_debug = True
    static_path = resource_filename("liteblue.apps", "static")
    procedures = "tests.app.procedures"
    alembic_script_location = "tests/alembic"
    db_url = os.getenv("DB_URL", "sqlite:///tests/test.db")
    connection_kwargs = config.Config.SQLITE_CONNECT_ARGS


class _Prod(_Config):
    """ mysql and redis config """

    db_url = "mysql+pymysql://root:secret@localhost:3309/simple"
    connection_kwargs = config.Config.MYSQL_CONNECT_ARGS
    connection_kwargs["echo"] = True
    redis_url = "redis://localhost:6381"


class _Remote(_Prod):
    """ used to test redis worker """

    redis_workers = 1


class _Docker(_Remote):

    procedures = "app.procedures"
    redis_url = "redis://liteblue-redis"
    db_url = "mysql+pymysql://root:secret@liteblue-db/simple"


Config = _Config
