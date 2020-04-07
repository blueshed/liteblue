""" simple functions """
import asyncio
import sys
from typing import Dict, NewType
from liteblue import current_user, broadcast
from liteblue.describe import describe


__all__ = ["add", "a_add", "say", "exceptional", "get_user", "reflect"]


def add(a: int, b: int) -> int:
    """ returns a plus b """
    return a + b


async def a_add(a: int, b: int, nap: float = 0.01) -> int:
    """ returns a plus b """
    await asyncio.sleep(nap)
    return a + b


def say(what: "typing.Any") -> None:
    """ broadcast your say to everyone """
    user = current_user()["email"].split("@")[0]
    broadcast({"action": "said", "message": f"{user} says: {what!r}"})


def exceptional(message: str) -> "None":
    """ raises exception with message """
    raise Exception(message)


User = Dict[str, str]


def get_user() -> User:
    """ returns the current user """
    return current_user()


Reflection = NewType("Reflection", dict)


def reflect() -> Reflection:
    """ describes available procedures """
    return describe(sys.modules[__name__], __all__)
