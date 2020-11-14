# pylint: disable=W0201
"""
    Support for Tornado Authentication.
"""
import logging
from tornado.web import RequestHandler, HTTPError
from tornado.ioloop import IOLoop
from .user_mixin import UserMixin


class LogoutHandler(UserMixin, RequestHandler):  # pylint: disable=W0223
    """
    Removes the cookie from application settings
    and redirects.
    """

    def get(self):
        """ removes cookie and redirects to optional next argument """
        self.set_current_user(None)
        self.redirect(self.get_argument("next", "/"))


class LoginHandler(UserMixin, RequestHandler):  # pylint: disable=W0223
    """
    Can be called as ajax from the
    websocket client to get the auth cookie
    into the headers.
    """

    def initialize(self, login, register, page="login.html"):
        """ we're configured with functions to perform login and register """
        self.login = login
        self.register = register
        self.page = page

    def get(self, error=None, notice=None):
        """ render the form """
        email = self.get_argument("email", default=None)
        next_ = self.get_argument("next", "/")
        can_register = self.register is not None
        self.render(
            self.page,
            email=email,
            error=error,
            notice=notice,
            next=next_,
            can_register=can_register,
            app_name=self.settings.get("app_name", "liteblue"),
        )

    async def post(self):
        """ handle login post """
        try:
            email = self.get_argument("email", None)
            password = self.get_argument("password", None)
            submit = self.get_argument("submit", "login")
            if email is None or password is None:
                raise HTTPError(403, "email or password is None")

            loop = IOLoop.current()
            user = None
            if submit == "login":
                user = await loop.run_in_executor(None, self.login, email, password)
            elif self.register:
                user = await loop.run_in_executor(None, self.register, email, password)
            if user:
                self.set_current_user(user)
                self.redirect(self.get_argument("next", "/"))
            else:
                raise Exception("email or password incorrect")
        except Exception as ex:  # pylint: disable=W0703
            logging.exception(ex)
            self.get(error=str(ex))
