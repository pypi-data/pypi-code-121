# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing
from requests.models import Response as HttpResponse

from shapelets.services.login_service_support import (
    _get_salt_pk,
    _sign_nonce,
    _extract_cookies
)
from shapelets.services.base_service import BaseService
from shapelets.services.exceptions import ShapeletsLoginException


class Endpoint(Enum):
    _LOGIN_AUTH = "api/login/unp"
    REGISTER = f"{_LOGIN_AUTH}/register"
    PASSWORD = f"{_LOGIN_AUTH}/password"
    CHECK = f"{_LOGIN_AUTH}/check"
    AUTHENTICATE = f"{_LOGIN_AUTH}/authenticate"
    USER_CHALLENGE = f"{_LOGIN_AUTH}/challenge?userName=###username###"

    def replace(self, username: str) -> str:
        template = str(self.value)
        return template.replace("###username###", username)


class LoginService(BaseService):
    """
    Provides methods for user login management and authentication.
    """

    def __init__(self, address: str, port: int = None):
        super().__init__(f"{address}:{port}" if port else address, None)

    def register_user(self, username: str, password: str) -> None:
        """
        Registers a new user and returns a ShapeletsLogin instance.
        :param username: Username of the logged user.
        :param password: Password of the logged user.
        :return: A ShapeletsLogin instance.
        """
        salt, public = _get_salt_pk(password)
        self.request_post(
            Endpoint.REGISTER.value,
            {
                "userName": username,
                "salt": list(salt),
                "pk": list(public)
            },
            ShapeletsLoginException
        )
        return self.login_user(username, password)

    def login_user(self, username: str, password: str) -> None:
        """
        Logs in a user and returns a ShapeletsLogin instance.
        :param username: Username of the logged user.
        :param password: Password of the logged user.
        :return: A ShapeletsLogin instance.
        """
        challenge_data = self._get_challenge(username)
        signature = _sign_nonce(password, challenge_data)
        auth_response = self._authenticate_user(challenge_data["userName"], signature)
        self.cookies = _extract_cookies(auth_response)

    def update_password(self, username: str, password: str, new_password) -> bool:
        """
        Updates the user's password.
        :param username: Username of the logged user.
        :param password: Password of the logged user.
        :param new_password: New password for the logged user.
        :return: True if the password was updated.
        """
        challenge_data = self._get_challenge(username)
        signature = _sign_nonce(password, challenge_data)
        salt, public = _get_salt_pk(new_password)
        self.request_put(
            Endpoint.PASSWORD.value,
            {
                "userDetails": {
                    "userName": username,
                    "salt": list(salt),
                    "pk": list(public)
                },
                "challengeResponse": {
                    "userName": username,
                    "token": list(signature),
                    "associateToCurrentUser": False,
                    "rememberMe": False
                }
            },
            ShapeletsLoginException
        )
        return True

    def check_username_is_available(self, username):
        """
        Checks whether username already exists as a registered user.
        :param username: Username to check.
        :return: True if the username is registered.
        """
        try:
            self.request_post(
                Endpoint.CHECK.value,
                username,
                ShapeletsLoginException)
            return True
        except ShapeletsLoginException:
            return False

    def check_server_is_up(self):
        self._get_challenge('admin')


    def _get_challenge(self, username: str) -> typing.Dict:
        """
        Retrieves and returns a login challenge.
        :return: The challenge to solve (dict keys: 'userName', 'salt', 'nonce').
        """
        return self.request_get(
            Endpoint.USER_CHALLENGE.replace(username),
            ShapeletsLoginException)

    def _authenticate_user(self, username: str, signature: bytes) -> HttpResponse:
        return self.request_post(
            Endpoint.AUTHENTICATE.value,
            {
                "userName": username,
                "token": list(signature),
                "associateToCurrentUser": False,
                "rememberMe": False
            },
            ShapeletsLoginException,
            with_headers=True)
