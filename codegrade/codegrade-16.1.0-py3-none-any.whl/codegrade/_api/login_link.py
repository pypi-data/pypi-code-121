"""The endpoints for login_link objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.assignment_login_link import AssignmentLoginLink
    from ..models.result_data_post_login_link_login import (
        ResultDataPostLoginLinkLogin,
    )


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class LoginLinkService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get(
        self,
        *,
        login_link_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AssignmentLoginLink":
        """Get a login link and the connected assignment.

        :param login_link_id: The id of the login link you want to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested login link, which will also contain information
                  about the connected assignment.
        """

        url = "/api/v1/login_links/{loginLinkId}".format(
            loginLinkId=login_link_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.assignment_login_link import AssignmentLoginLink

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AssignmentLoginLink)
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

    def login(
        self,
        *,
        login_link_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ResultDataPostLoginLinkLogin":
        """Login with the given login link.

        This will only work when the assignment connected to this link is
        available, and the lock date has not expired. The received JWT token
        will only be valid until the 30 minutes after the lock date, and only
        in the course connected to this link.

        The scope of the returned token will change in the future, this will
        not be considered a breaking change.

        :param login_link_id: The id of the login link you want to use to
            login.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The logged in user and an access token.
        """

        url = "/api/v1/login_links/{loginLinkId}/login".format(
            loginLinkId=login_link_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.result_data_post_login_link_login import (
                ResultDataPostLoginLinkLogin,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ResultDataPostLoginLinkLogin)
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
