""" fixtures for testing """
import asyncio
import pytest
import aioredis
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from .app.main import Config as settings
from liteblue import context
from liteblue.server import Application
from liteblue.connection import ConnectionMgr
from liteblue.handlers import BroadcastMixin


def is_mysql_responsive(url):
    print("connecting to: ", url)
    try:
        conn = sa.create_engine(url)
        conn.execute("select now()")
        return True
    except sa.exc.OperationalError:
        return False


@pytest.fixture(scope="session")
def db_url(docker_services):
    """Ensure that mysql is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    mysql_port = docker_services.port_for("liteblue-db", 3306)
    url = f"mysql+pymysql://root:secret@localhost:{mysql_port}/simple"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.5, check=lambda: is_mysql_responsive(url)
    )
    return url


async def is_redis_responsive(url):
    try:
        redis = await aioredis.create_redis_pool(url)
        await redis.set("my-key", "value")
        val = await redis.get("my-key", encoding="utf-8")
        assert val == "value"
        redis.close()
        await redis.wait_closed()
        return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def redis_url(docker_services):
    """Ensure that redis is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    redis_port = docker_services.port_for("liteblue-redis", 6379)
    url = f"redis://localhost:{redis_port}"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.5,
        check=lambda: asyncio.run(is_redis_responsive(url)),
    )
    return url


@pytest.fixture(scope="session")
def default_db(db_url):
    """ Use alembic to get our db into a known state """

    alembic_config = Config()
    alembic_config.set_main_option("sqlalchemy.url", db_url)
    alembic_config.set_main_option("script_location", settings.alembic_script_location)
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    ConnectionMgr.connection("default", db_url)
    yield "default"


@pytest.fixture
def no_login_url():
    login_url = settings.tornado_login_url
    settings.tornado_login_url = None
    yield
    settings.tornado_login_url = login_url


@pytest.fixture
def app(default_db, io_loop):
    """ returns a testable app """

    app = Application(settings)  # a tornado.web.Application
    yield app
