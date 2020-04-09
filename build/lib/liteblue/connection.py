""" A connection to a sqlalchemy db """
import logging
import threading
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

LOGGER = logging.getLogger(__name__)


class NoConnection(Exception):
    """ raised on missing execption """


@contextmanager
def scoped_session(session_cls):
    """Provide a transactional scope around a series of operations."""
    session = session_cls()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class ConnectionMgr:
    """

    Provides thread safe named access to sqlalchemy sessions

    first declare your connection::

        ConnectionMgr.connection("default", "sqlite:///simple.db")

    then connect::

        with ConnectionMgr.session("default") as session:
            session.execute(sql.insert(role, {"name": "user"}))
            session.commit()

    """

    connections = {}
    connections_lock = threading.Lock()

    @classmethod
    def connection(cls, name, db_url, **kwargs):
        """
        creates a cached engine and session_cls for db_url
        kwargs are passed on the create_engine
        """
        with cls.connections_lock:
            conn = cls.connections.get(name)
            if conn is None:
                engine = create_engine(db_url, **kwargs)
                session_cls = sessionmaker(bind=engine)
                conn = engine, session_cls
                cls.connections[name] = conn
                LOGGER.info("%s connection available", name)
        return conn[0], conn[1]

    @classmethod
    def session(cls, name="default"):
        """
        returns a contextmanager awair session
        with autocommit disabled.
        """
        conn = cls.connections.get(name)

        if conn is None:
            raise NoConnection(f"No connection {name} - check configuration")

        return scoped_session(conn[1])
