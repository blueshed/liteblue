""" Test redis connection and setup """
import asyncio
import json
import logging
import urllib.parse
import pytest
from tornado.httpclient import HTTPRequest, HTTPClientError
from tornado.websocket import websocket_connect, WebSocketClosedError
from .helpers import SimpleBroadcaster


def test_redis_url(redis_url):
    """ get the connection url for redis """
    print(redis_url)
    assert redis_url == "redis://localhost:6381"


async def test_broadcaster(redis_url, io_loop, caplog):
    """ test broadcaster """
    with caplog.at_level(logging.DEBUG, logger="simpler.broadcaster"):
        broadcaster = SimpleBroadcaster("test_broadcast", redis_url)
        io_loop.call_later(0, broadcaster.subscribe)
        await asyncio.sleep(0.1)  # allow subscription

        await broadcaster.publish("what")
        await asyncio.sleep(0.2)  # allow reciept

        assert len(broadcaster.documents) == 1

        await broadcaster.unsubscribe()


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
                "email": "redis-rpc@ws.com",
                "password": "12345",
                "submit": "register",
            }
        ),
        follow_redirects=False,
        raise_error=False,
    )
    return response.headers["Set-Cookie"]


@pytest.fixture
async def ws_client(http_server_port, cookie):

    request = HTTPRequest(
        f"ws://localhost:{http_server_port[1]}/ws",
        headers={"Cookie": await cookie},
    )
    result = await websocket_connect(request)
    return result


async def test_redis_broadcast(ws_client, redis_url, io_loop, app):
    """ test add function via websocket """
    from liteblue.handlers import BroadcastMixin
    import time

    BroadcastMixin.init_broadcasts(io_loop, f"test-{time.time}-topic", redis_url)

    client = await ws_client

    message = {"jsonrpc": "2.0", "method": "say", "params": ["hi there"]}
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response) == {
        "action": "said",
        "message": "redis-rpc says: 'hi there'",
    }

    client.close()
    await app.tidy_up()
