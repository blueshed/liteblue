import urllib
import logging
import json
import pytest
from tornado.httpclient import HTTPRequest, HTTPClientError


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
                "email": "post-rpc@ws.com",
                "password": "12345",
                "submit": "register",
            }
        ),
        follow_redirects=False,
        raise_error=False,
    )
    return response.headers["Set-Cookie"]


async def test_add_post(http_server_client, cookie, caplog):
    """ test add function via websocket """

    with caplog.at_level(logging.DEBUG):

        response = await http_server_client.fetch(
            "/rpc",
            headers={"Cookie": await cookie},
            method="POST",
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "1a",
                    "method": "add",
                    "params": [2, 2],
                }
            ),
        )
        assert json.loads(response.body)["result"] == 4


async def test_add_post_fails(http_server_client, caplog):
    """ test add function via websocket """

    with caplog.at_level(logging.DEBUG):

        response = await http_server_client.fetch(
            "/rpc",
            method="POST",
            body=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "1a",
                    "method": "add",
                    "params": [2, 2],
                }
            ),
            follow_redirects=False,
            raise_error=False,
        )
        assert response.code == 403
