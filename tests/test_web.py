""" test the web server """
import urllib.parse
from tornado.httpclient import HTTPClientError
from sqlalchemy.sql import insert
from liteblue import ConnectionMgr
from liteblue.user import user


async def test_login(http_server_client):
    resp = await http_server_client.fetch("/login")
    assert resp.code == 200

    try:
        resp = await http_server_client.fetch("/", follow_redirects=False)
        assert resp.code == 302
    except HTTPClientError as ex:
        assert ex.code == 302


async def test_register_fail(http_server_client):
    body = urllib.parse.urlencode(
        {"email": "boo@hoo.com", "password": "1234", "submit": "register"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    response = await http_server_client.fetch(
        "/login", headers=headers, method="POST", body=body, follow_redirects=False,
    )
    assert "Password must be five or more characters" in response.body.decode("utf-8")


async def test_register(http_server_client):
    body = urllib.parse.urlencode(
        {"email": "boo@hoo.com", "password": "12345", "submit": "register"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    try:
        await http_server_client.fetch(
            "/login", headers=headers, method="POST", body=body, follow_redirects=False,
        )
    except HTTPClientError as ex:
        print(ex.response.headers)
        cookie = ex.response.headers["Set-Cookie"]
        assert ex.code == 302

    resp = await http_server_client.fetch("/", headers={"Cookie": cookie})
    assert resp.code == 200


async def test_pre_register(http_server_client, default_db):
    """ test the user pre registered no password """
    with ConnectionMgr.session(default_db) as session:
        session.execute(insert(user, {"email": "boop@test.com"}))
        session.commit()

    body = urllib.parse.urlencode(
        {"email": "boop@test.com", "password": "12345", "submit": "register"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    try:
        await http_server_client.fetch(
            "/login", headers=headers, method="POST", body=body, follow_redirects=False,
        )
    except HTTPClientError as ex:
        print(ex.response.headers)
        cookie = ex.response.headers["Set-Cookie"]
        assert ex.code == 302

    resp = await http_server_client.fetch("/", headers={"Cookie": cookie})
    assert resp.code == 200


async def test_register_already_fail(http_server_client):
    body = urllib.parse.urlencode(
        {"email": "boo@hoo.com", "password": "12345", "submit": "register"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    response = await http_server_client.fetch(
        "/login", headers=headers, method="POST", body=body, follow_redirects=False,
    )
    assert "Already registered" in response.body.decode("utf-8")


async def test_login_fail_no_email(http_server_client):
    body = {"password": "12345", "submit": "login"}
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    response = await http_server_client.fetch(
        "/login",
        headers=headers,
        method="POST",
        body=urllib.parse.urlencode(body),
        follow_redirects=False,
    )
    assert "email or password is None" in response.body.decode("utf-8")


async def test_login_fail_no_password(http_server_client):
    body = {"email": "boo@hoo.com", "submit": "login"}
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    response = await http_server_client.fetch(
        "/login",
        headers=headers,
        method="POST",
        body=urllib.parse.urlencode(body),
        follow_redirects=False,
    )
    assert "email or password is None" in response.body.decode("utf-8")


async def test_login_fail_no_user(http_server_client):
    body = {"email": "boo@hoo.com", "password": "54321", "submit": "login"}
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    response = await http_server_client.fetch(
        "/login",
        headers=headers,
        method="POST",
        body=urllib.parse.urlencode(body),
        follow_redirects=False,
    )
    assert "email or password incorrect" in response.body.decode("utf-8")


async def test_home_page(http_server_client):
    body = urllib.parse.urlencode(
        {"email": "boo@hoo.com", "password": "12345", "submit": "login"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    try:
        await http_server_client.fetch(
            "/login", headers=headers, method="POST", body=body, follow_redirects=False,
        )
    except HTTPClientError as ex:
        print(ex.response.headers)
        cookie = ex.response.headers["Set-Cookie"]
        assert ex.code == 302

    resp = await http_server_client.fetch("/", headers={"Cookie": cookie})
    assert resp.code == 200


async def test_logout(http_server_client):
    body = urllib.parse.urlencode(
        {"email": "boo@hoo.com", "password": "12345", "submit": "login"}
    )
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    try:
        await http_server_client.fetch(
            "/login", headers=headers, method="POST", body=body, follow_redirects=False,
        )
    except HTTPClientError as ex:
        print(ex.response.headers)
        cookie = ex.response.headers["Set-Cookie"]
        assert ex.code == 302

    resp = await http_server_client.fetch("/", headers={"Cookie": cookie})
    assert resp.code == 200

    try:
        await http_server_client.fetch(
            "/logout", headers=headers, method="GET", follow_redirects=False
        )
    except HTTPClientError as ex:
        print(ex.response.headers)
        cookie = ex.response.headers["Set-Cookie"]
        assert cookie.startswith('liteblue-app-user="";')
        assert ex.code == 302


async def test_public_access(no_login_url, http_server_client):
    """ test without login_url """
    resp = await http_server_client.fetch("/")
    assert resp.code == 200
