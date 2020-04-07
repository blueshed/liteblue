# pylint: disable=C0103
""" sqlalchemy tables """
from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey


metadata = MetaData()


activity_roles = Table(
    "activity_roles",
    metadata,
    Column("roles_id", Integer, ForeignKey("activity.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(128), nullable=False, doc="required"),
    Column("password", String(64), doc="and no longer"),
    Column("role_id", Integer, ForeignKey("role.id")),
)


activity = Table(
    "activity",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), unique=True),
)


role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255)),
)
