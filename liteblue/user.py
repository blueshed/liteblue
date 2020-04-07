# pylint: disable=C0103, W0401, W0614
""" sqlalchemy schema """
from sqlalchemy import *


metadata = MetaData()


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(128), nullable=False, unique=True, doc="required"),
    Column("password", String(64), doc="and no longer"),
)
