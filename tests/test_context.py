""" test context in thread and async """
import asyncio
from concurrent.futures import ThreadPoolExecutor
from liteblue import context
from liteblue import moo


def test_context():
    user = {"name": "foobert"}
    with moo._user_call_(user):
        assert context.current_user() == user


def is_user(user):
    assert context.current_user() == user


async def ais_user(user):
    is_user(user)


async def test_is_user(io_loop):
    user = {"name": "dogbert"}
    with ThreadPoolExecutor(max_workers=1) as executor:
        with moo._user_call_(user):
            await io_loop.run_in_executor(executor, is_user, None)
            await io_loop.run_in_executor(executor, test_context)
            await asyncio.sleep(0.01)
            await ais_user(user)
