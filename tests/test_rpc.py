""" Test rpc handler """
import asyncio
import json
import logging
import pytest
import urllib.parse
from tornado.httpclient import HTTPRequest, HTTPClientError
from tornado.websocket import websocket_connect, WebSocketClosedError
from liteblue import handlers


async def test_register(http_server_client):
    """ register user used in all subsrquent tests """
    body = urllib.parse.urlencode(
        {"email": "rpc@ws.com", "password": "12345", "submit": "register"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    try:
        await http_server_client.fetch(
            "/login",
            headers=headers,
            method="POST",
            body=body,
            follow_redirects=False,
        )
    except HTTPClientError as ex:
        assert ex.code == 302


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
            {"email": "rpc@ws.com", "password": "12345", "submit": "login"}
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


async def test_login_fail(http_server_client, http_server_port, io_loop, caplog):
    handlers.BroadcastMixin.io_loop = io_loop

    with caplog.at_level(logging.DEBUG):
        ws_url = f"ws://localhost:{http_server_port[1]}/ws"
        client = await websocket_connect(ws_url)
        try:
            message = {
                "jsonrpc": "2.0",
                "id": "1a",
                "method": "add",
                "params": [2, 2],
            }
            await client.write_message(json.dumps(message))
        except WebSocketClosedError:
            # we're not logged in
            pass
        client.close()
        await asyncio.sleep(0.01)


async def test_add(ws_client, caplog):
    """ test add function via websocket """

    client = await ws_client

    with caplog.at_level(logging.DEBUG):

        message = {
            "jsonrpc": "2.0",
            "id": "1a",
            "method": "add",
            "params": [2, 2],
        }
        await client.write_message(json.dumps(message))
        response = await client.read_message()
        print(response)
        assert json.loads(response)["result"] == 4

    client.close()
    await asyncio.sleep(0.01)


async def test_a_add(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {
        "jsonrpc": "2.0",
        "id": "1a",
        "method": "a_add",
        "params": {"a": 2, "b": 2},
    }
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["result"] == 4
    client.close()
    await asyncio.sleep(0.01)


async def test_no_such_func(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {
        "jsonrpc": "2.0",
        "id": "1a",
        "method": "b_add",
        "params": {"a": 2, "b": 2},
    }
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["error"]["message"] == "no such method: b_add"
    client.close()
    await asyncio.sleep(0.01)


async def test_private_func(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {
        "jsonrpc": "2.0",
        "id": "1a",
        "method": "_add",
        "params": {"a": 2, "b": 2},
    }
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["error"]["message"] == "method private"
    client.close()
    await asyncio.sleep(0.01)


async def test_method_missing(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {"jsonrpc": "2.0", "id": "1a", "params": {"a": 2, "b": 2}}
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["error"]["message"] == "no method"
    client.close()
    await asyncio.sleep(0.01)


async def test_wrong_protocol(ws_client):
    """ test add function via websocket """

    client = await ws_client

    try:
        message = {
            "jsonrpc": "1.0",
            "id": "1a",
            "method": "add",
            "params": [2, 2],
        }
        await client.write_message(json.dumps(message))
        response = await client.read_message()
        print(response)
        assert json.loads(response)["error"]["message"] == "protocol not supported"

    finally:
        client.close()
        await asyncio.sleep(0.01)


async def test_wrong_params(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {"jsonrpc": "2.0", "id": "1a", "method": "add", "params": 2}
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["error"]["message"] == "Params neither list or dict"
    client.close()
    await asyncio.sleep(0.01)


async def test_broadcast(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {"jsonrpc": "2.0", "method": "say", "params": ["hi there"]}
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response) == {
        "action": "said",
        "message": "rpc says: 'hi there'",
    }
    client.close()
    await asyncio.sleep(0.01)


async def test_exceptional(ws_client):
    """ test add function via websocket """

    client = await ws_client

    message = {
        "jsonrpc": "2.0",
        "id": "1a",
        "method": "exceptional",
        "params": ["hi there"],
    }
    await client.write_message(json.dumps(message))
    response = await client.read_message()
    print(response)
    assert json.loads(response)["error"] == {
        "code": -32000,
        "message": "hi there",
    }
    client.close()
    await asyncio.sleep(0.01)


async def test_keep_alive(ws_client, caplog):
    """ test add function via websocket """

    client = await ws_client

    with caplog.at_level(logging.DEBUG):

        handlers.BroadcastMixin.keep_alive()
        await asyncio.sleep(0.1)
        client.close()

        await asyncio.sleep(0.1)
