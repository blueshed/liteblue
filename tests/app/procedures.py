""" simple functions """
import asyncio
import sys
import time
import uuid
import logging
from functools import partial
from sqlalchemy import sql
from typing import Dict, NewType
from liteblue import context
from liteblue.connection import ConnectionMgr
from liteblue.describe import describe, describe_sql
from . import tables

LOGGER = logging.getLogger(__name__)

__all__ = [
    "add",
    "a_add",
    "say",
    "exceptional",
    "get_user",
    "users",
    "reflect",
    "start_service",
    "stop_service",
    "list_services",
]


def add(a: int, b: int) -> int:
    """ returns a plus b """
    return a + b


async def a_add(a: int, b: int, nap: float = 0.01) -> int:
    """ returns a plus b """
    await asyncio.sleep(nap)
    return a + b


def say(what: "typing.Any") -> None:
    """ broadcast your say to everyone """
    user = context.current_user()["email"].split("@")[0]
    context.broadcast({"action": "said", "message": f"{user} says: {what!r}"})


def exceptional(message: str) -> "None":
    """ raises exception with message """
    raise Exception(message)


User = Dict[str, str]


def get_user() -> User:
    """ returns the current user """
    return context.current_user()


Reflection = NewType("Reflection", dict)


async def reflect() -> dict:
    """ describes available procedures """
    return {
        "procedures": describe(sys.modules[__name__], __all__),
        "tables": describe_sql(tables.metadata),
    }


def users() -> list:
    """ returns a list of users """
    with ConnectionMgr.session() as session:
        start = time.time()
        rows = session.execute(
            sql.select([tables.user.c.email, tables.role.c.name]).select_from(
                tables.user.outerjoin(
                    tables.role, tables.user.c.role_id == tables.role.c.id
                )
            )
        )
        activities = {}
        result = []
        for row in rows:
            result.append(dict(user=row.email, role=row.name))
            activities[row.name] = []
        rows = session.execute(
            sql.select(
                [
                    tables.role.c.name.label("role"),
                    tables.activity.c.name.label("activity"),
                ],
                tables.role.c.name.in_(activities),
            ).select_from(
                tables.activity_roles.join(
                    tables.activity,
                    tables.activity.c.id == tables.activity_roles.c.roles_id,
                ).join(
                    tables.role,
                    tables.role.c.id == tables.activity_roles.c.role_id,
                )
            )
        )
        for row in rows:
            if row.activity:
                activities[row.role].append(row.activity)
        for item in result:
            item["activities"] = activities[item["role"]]
        result.append(time.time() - start)
        return result


async def service(
    action: str = "set_broadcast",
    message: "typing.Any" = "hoho",
    delay: int = 30,
):
    try:
        LOGGER.info("starting service...")
        while True:
            await asyncio.sleep(delay)
            context.broadcast({"action": action, "message": message})
    except asyncio.CancelledError:
        LOGGER.info("cancelled service.")
        pass
    LOGGER.info("stopped service.")


TASKS = {}


def service_done(task):
    """ removes a task from TASKS """
    LOGGER.info("removing: %r", task)
    del TASKS[task.get_name()]


async def start_service(name: str, args: list) -> str:
    """ start service and return its name """
    LOGGER.info("start service: %s %r", name, args)
    coro = globals()[name]
    LOGGER.info("service: %r", coro)
    task_name = str(uuid.uuid4())
    task = asyncio.create_task(coro(*args), name=task_name)
    task.add_done_callback(service_done)
    TASKS[task_name] = task
    return task_name


async def stop_service(name: str) -> None:
    """ stop service """
    task = TASKS.get(name)
    if task is None:
        raise Exception(f"No such task {name}")
    return task.cancel()


def list_services() -> list:
    """ list running services """
    return [task.get_name() for task in TASKS.values()]
