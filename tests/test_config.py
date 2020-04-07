from liteblue.config import Config


class Overide(Config):
    """ can we overide ? """

    tornado_login_url = ""


def test_config():
    assert Config.tornado_login_url == "/login"


def test_overide():
    assert Overide.tornado_login_url == ""
