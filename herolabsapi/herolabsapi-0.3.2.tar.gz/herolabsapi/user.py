"""Define an API endpoint manager for user data & actions."""
from __future__ import annotations

import json
from typing import Awaitable, Callable

from herolabsapi import USER_RESOURCE, RESET_PASSWORD_RESOURCE


class User:
    """Define the user manager object."""

    def __init__(self, async_request: Callable[..., Awaitable], user_id: str) -> None:
        """Initialize."""
        self._async_request = async_request
        self._user_id: str = user_id

    async def async_get_user_details(self) -> dict:
        """Return the user details."""
        user_details_url = f"{USER_RESOURCE}{self._user_id}"
        return await self._async_request("get", user_details_url)

    async def async_update_user_details(self, user_updates_payload: str) -> None:
        """Update the user details.
        For multiple changes use comma separation dictionary {'last_name': 'testLastName', 'language': 'en'}
        These are passed as arguments in the function.
        The updatable options are "email", "first_name", "last_name", "phone" (e.g "+447712345678")
        & "language" (passed as a language value i.e "en", "pl")"""
        update_user_details_url = f"{USER_RESOURCE}{self._user_id}"
        return await self._async_request("put", update_user_details_url, data=json.dumps(user_updates_payload))

    async def async_reset_password_request(self, user_email: str) -> str:
        """Requests reset password email with further instructions."""
        await self._async_request("post", RESET_PASSWORD_RESOURCE, json={"email": f"{user_email}"})
        return "Password reset email has been requested"
