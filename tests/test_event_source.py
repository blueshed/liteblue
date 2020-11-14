import asyncio
import logging
import urllib.parse
import pytest
import tornado.iostream
import tornado.simple_httpclient
from liteblue.moo import Moo
from liteblue import context
from tests.app.main import Config


@pytest.fixture
async def cookie(http_server_client):
    response = await http_server_client.fetch(
        "/login",
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain",
        },
        method="POST",
        body=urllib.parse.urlencode(
            {
                "email": "evts-rpc@ws.com",
                "password": "12345",
                "submit": "register",
            }
        ),
        follow_redirects=False,
        raise_error=False,
    )
    return response.headers["Set-Cookie"]


async def test_event_source(io_loop, http_server_client, cookie, caplog):

    with caplog.at_level(logging.DEBUG):

        def callback(chunk):
            logging.debug("got %s", chunk)
            assert b"moo says:" in chunk

        async def say_something():
            async with Moo(
                Config, io_loop=io_loop, user={"email": "moo@cow.farm"}
            ) as cow:
                await cow.say("hi")
            logging.debug("done said")

        async def listen():
            logging.debug("listening")
            try:
                await http_server_client.fetch(
                    "/events",
                    headers={"Cookie": await cookie},
                    streaming_callback=callback,
                )
            except tornado.iostream.StreamClosedError:
                pass
            except tornado.simple_httpclient.HTTPStreamClosedError:
                pass
            logging.debug("done listening")

        io_loop.add_callback(listen)
        await asyncio.sleep(0.05)
        io_loop.add_callback(say_something)
        await asyncio.sleep(0.1)
