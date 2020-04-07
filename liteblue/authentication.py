"""
    Support for Tornado Authentication.
"""
import hashlib
from sqlalchemy.sql import select, insert, update, and_
from .connection import ConnectionMgr
from .user import user


def login(email: str, password: str):
    """ hash the password and see if you can find the user """
    hex_key = hashlib.md5(password.encode("utf-8")).hexdigest()
    with ConnectionMgr.session() as session:
        row = session.execute(
            select([user], and_(user.c.email == email, user.c.password == hex_key))
        ).first()
        result = None
        if row:
            result = dict(row)
            del result["password"]
        return result


def register(email: str, password: str):
    """ hash the password and save the new user """
    if len(password) < 5:
        raise Exception("Password must be five or more characters")
    hex_key = hashlib.md5(password.encode("utf-8")).hexdigest()
    with ConnectionMgr.session() as session:
        where = user.c.email == email
        row = session.execute(select([user], where)).first()
        if row is None:
            user_dict = {"email": email}
        else:
            if row["password"]:
                raise Exception("Already registered")
            user_dict = dict(row)
        user_dict["password"] = hex_key
        if user_dict.get("id"):
            where = user.c.id == user_dict["id"]
            values = {k: v for k, v in user_dict.items() if k != "id"}
            session.execute(update(user, where, values))
        else:
            user_dict["id"] = session.execute(
                insert(user, user_dict)
            ).inserted_primary_key[0]
        session.commit()
        del user_dict["password"]
        return user_dict
