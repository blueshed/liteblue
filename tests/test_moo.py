import logging
from liteblue.moo import Moo
from tests.app.main import Config


async def test_app(io_loop, caplog):
    """ can we do a local add """
    with caplog.at_level(logging.DEBUG):
        async with Moo(Config, io_loop) as moo:
            assert await moo.add(2, 2) == 4
            try:
                await moo.foo()
                assert False, 'there is no method "foo"'
            except AttributeError:
                pass
