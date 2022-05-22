import asyncio
import webbrowser
from datetime import timedelta
from typing import Any, Dict, Iterable, Optional, TypeVar

from classiq._internals.async_utils import poll_for
from classiq._internals.authentication.auth0 import Auth0, Tokens
from classiq.exceptions import ClassiqAuthenticationError, ClassiqExpiredTokenError

T = TypeVar("T")


class DeviceRegistrar:
    _TIMEOUT_ERROR = (
        "Device registration timed out. Please re-initiate the flow and "
        "authorize the device within the timeout."
    )
    _TIMEOUT_SEC: float = timedelta(minutes=15).total_seconds()

    @classmethod
    async def register(cls, get_refresh_token: bool = True) -> Tokens:
        data: Dict[str, Any] = await Auth0.get_device_data(
            get_refresh_token=get_refresh_token
        )

        print(f"Your user code: {data['user_code']}")
        verification_url = data["verification_uri_complete"]
        print(
            f"If a browser doesn't automatically open, please visit the url: {verification_url}"
        )
        webbrowser.open(verification_url)
        timeout = min(data["expires_in"], cls._TIMEOUT_SEC)
        return await cls._poll_tokens(
            device_code=data["device_code"],
            interval=data["interval"],
            timeout=timeout,
            get_refresh_token=get_refresh_token,
        )

    @classmethod
    def _handle_ready_data(
        cls, data: Dict[str, Any], get_refresh_token: bool
    ) -> Tokens:
        access_token: Optional[str] = data.get("access_token")
        # If refresh token was not requested, this would be None
        refresh_token: Optional[str] = data.get("refresh_token")

        if access_token is None or (
            get_refresh_token is True and refresh_token is None
        ):
            raise ClassiqAuthenticationError(
                "Token generation failed for unknown reason."
            )

        return Tokens(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    async def _poll_tokens(
        cls,
        device_code: str,
        interval: int,
        timeout: int,
        get_refresh_token: bool = True,
    ) -> Tokens:
        async def poller():
            nonlocal device_code
            return await Auth0.poll_tokens(device_code=device_code)

        def interval_coro() -> Iterable[int]:
            nonlocal interval
            while True:
                yield interval

        await asyncio.sleep(interval)
        async for data in poll_for(
            poller=poller, timeout_sec=timeout, interval_sec=interval_coro()
        ):
            error_code: Optional[str] = data.get("error")
            if error_code is None:
                return cls._handle_ready_data(data, get_refresh_token)
            elif error_code == "authorization_pending":
                pass
            elif error_code == "slow_down":
                # This value is used by poll_for via interval_coro
                interval *= 2
            elif error_code == "expired_token":
                raise ClassiqExpiredTokenError(cls._TIMEOUT_ERROR)
            elif error_code == "access_denied":
                raise ClassiqAuthenticationError("Access denied.")
            else:
                raise ClassiqAuthenticationError(
                    f"Device registration failed with an unknown error: {error_code}."
                )
        else:
            raise ClassiqAuthenticationError(cls._TIMEOUT_ERROR)
