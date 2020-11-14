""" Test database connection and setup """
from sqlalchemy.sql import insert, update, delete, select
from liteblue.connection import ConnectionMgr, NoConnection
from .app.tables import user, role, activity, activity_roles
from .helpers import FauxException


def test_db_url(db_url):
    """ get the sqlalchemy connection url for db """
    print(db_url)
    assert db_url == "mysql+pymysql://root:secret@localhost:3309/simple"


def test_no_connection():
    """ test for connection that does not exist """
    try:
        with ConnectionMgr.session("no such session") as session:
            session.rollback()
            assert False, "should not get here"
    except NoConnection:
        pass


def test_rollback(default_db):
    """ test that exception causes rollback """
    try:
        with ConnectionMgr.session(default_db) as session:
            raise FauxException()
    except FauxException:
        pass


def test_user(default_db):
    """ test the user table """
    with ConnectionMgr.session() as session:
        session.execute(insert(user, {"email": "foo@test.com"}))
        session.commit()
        row = session.execute(select([user], user.c.email == "foo@test.com")).first()
        assert row.email == "foo@test.com"

        session.execute(update(user, user.c.id == row.id, {"email": "food@test.com"}))
        session.commit()
        row = session.execute(select([user], user.c.id == row.id)).first()
        assert row.email == "food@test.com"

        session.execute(delete(user, user.c.id == row.id))
        session.commit()
        row = session.execute(select([user], user.c.id == row.id)).first()
        assert row is None


def test_role_activities(default_db):
    """ test the role table """
    with ConnectionMgr.session() as session:
        role_ = {"name": "user"}
        role_["id"] = session.execute(insert(role, role_)).inserted_primary_key[0]
        activity_ = {"name": "login"}
        activity_["id"] = session.execute(
            insert(activity, activity_)
        ).inserted_primary_key[0]
        session.execute(
            insert(
                activity_roles,
                {"roles_id": activity_["id"], "role_id": role_["id"]},
            )
        )
        session.commit()

        role_ = dict(session.execute(select([role])).first())
        rows = session.execute(
            select([activity], activity_roles.c.role_id == role_["id"]).select_from(
                activity.join(
                    activity_roles, activity.c.id == activity_roles.c.roles_id
                )
            )
        )
        activities = [dict(row) for row in rows]
        assert role_["name"] == "user"
        assert activities[0] == activity_
        assert activities[0]["name"] == "login"
