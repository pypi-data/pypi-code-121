"""The endpoints for oauth_provider objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.oauth_provider import OAuthProvider
    from ..models.oauth_token import OAuthToken
    from ..models.setup_oauth_result import SetupOAuthResult


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class OAuthProviderService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self,
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[OAuthProvider]":
        """Get all OAuth providers connected to this instance.

        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All connected providers.
        """

        url = "/api/v1/oauth_providers/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.oauth_provider import OAuthProvider

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(OAuthProvider))
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def get_oauth_token(
        self: "OAuthProviderService[codegrade.client.AuthenticatedClient]",
        *,
        provider_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "OAuthToken":
        """Get an OAuth token for the specified provider.

        :param provider_id: The provider for which you want to get a token.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The token.
        """

        url = "/api/v1/oauth_providers/{providerId}/token".format(
            providerId=provider_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.oauth_token import OAuthToken

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(OAuthToken)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def put_oauth_token(
        self: "OAuthProviderService[codegrade.client.AuthenticatedClient]",
        *,
        provider_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[OAuthToken, SetupOAuthResult]":
        """Get or create an OAuth token for the specified provider.

        :param provider_id: The provider for which you want to get/create a
            token.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The token.
        """

        url = "/api/v1/oauth_providers/{providerId}/token".format(
            providerId=provider_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.oauth_token import OAuthToken
            from ..models.setup_oauth_result import SetupOAuthResult

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(OAuthToken),
                    parsers.ParserFor.make(SetupOAuthResult),
                )
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, "5XX"),
                    utils.unpack_union(AnyError),
                ),
            ),
        )
