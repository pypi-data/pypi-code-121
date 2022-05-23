import logging
from typing import Mapping

import okta_jwt_verifier
from okta_jwt_verifier.exceptions import JWTValidationException


logger = logging.getLogger(__name__)


class InvalidTokenException(Exception):
    pass


class AuthorisationManager:
    def __init__(
        self,
        service_name: str,
        okta_issuer: str,
        okta_audience: str,
    ):
        self._service_name = service_name
        self._jwt_verifier = okta_jwt_verifier.BaseJWTVerifier(issuer=okta_issuer, audience=okta_audience)

    async def _verify_token(self, cookies: Mapping):
        try:
            await self._jwt_verifier.verify_access_token(cookies["oktagon_access_token"])
        except JWTValidationException as exc:
            logger.error("Failed to validate access token: %s", exc)
            raise InvalidTokenException from JWTValidationException
        except KeyError:
            raise InvalidTokenException("No token provided!")

    async def get_user_email(self, cookies: Mapping) -> str:
        await self._verify_token(cookies)
        return self._jwt_verifier.parse_token(cookies["oktagon_access_token"])[1]["sub"]

    async def is_user_authorised(self, allowed_groups: list, resource_name: str, cookies: Mapping) -> bool:
        await self._verify_token(cookies)
        decoded_claims = self._jwt_verifier.parse_token(cookies["oktagon_access_token"])[1]

        try:
            return self.does_user_have_required_group(
                user_groups=decoded_claims["groups"],
                username=decoded_claims["sub"],
                resource_name=resource_name,
                allowed_groups=allowed_groups,
            )
        except KeyError as exc:
            raise InvalidTokenException("Groups or sub claims are not provided!") from exc

    def does_user_have_required_group(
        self, user_groups: list, username: str, allowed_groups: list, resource_name: str
    ) -> bool:
        if not any(allowed_group in user_groups for allowed_group in allowed_groups):
            logger.info(
                "%s is not allowed to access resource: %s in %s",
                username,
                resource_name,
                self._service_name,
            )
            return False

        logger.info(
            "%s is allowed to access resource: %s in %s",
            username,
            resource_name,
            self._service_name,
        )
        return True
