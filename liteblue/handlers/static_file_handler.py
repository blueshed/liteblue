"""
    We need authenticated access to static files
"""
from tornado.web import authenticated, StaticFileHandler
from .user_mixin import UserMixin


class AuthStaticFileHandler(UserMixin, StaticFileHandler):  # pylint: disable=W0223
    """
    This provide integration between tornado.web.authenticated
    and tornado.web.StaticFileHandler.

    It assumes you have set up the cookie name in the application
    settings and that the request already has the cookie set. In
    other words the user has already authenticated.
    """

    @authenticated
    async def get(self, path, include_body=True):
        """ safe to return what you need """
        return StaticFileHandler.get(self, path, include_body)
