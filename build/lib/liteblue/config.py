# pylint: disable=R0903
""" application configuration """
import os
from pkg_resources import resource_filename


class Config:
    """ Access to configuration """

    name = "liteblue-app"
    port = int(os.getenv("PORT", "8080"))
    max_workers = 5
    tornado_debug = False
    tornado_cookie_name = f"{name}-user"
    tornado_cookie_secret = f"it was dark and stormy night for {name}"
    tornado_login_url = "/login"
    static_path = resource_filename("liteblue.apps", "static")
    procedures = ".procedures"

    SQLITE_CONNECT_ARGS = {"echo": False, "encoding": "utf-8"}

    MYSQL_CONNECT_ARGS = {
        "echo": False,
        "isolation_level": "READ COMMITTED",
        "pool_recycle": 120,
        "pool_size": max_workers,
        "encoding": "utf-8",
    }
    alembic_script_location = "alembic"
    db_url = os.getenv("DB_URL", f"sqlite:///{name}.db")
    connection_kwargs = SQLITE_CONNECT_ARGS

    redis_url = None
    redis_topic = f"{name}-broadcast"
