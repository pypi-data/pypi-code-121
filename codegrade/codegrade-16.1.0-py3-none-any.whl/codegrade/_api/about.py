"""The endpoints for about objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.about import About


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class AboutService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get(
        self,
        *,
        health: Maybe["str"] = Nothing,
        tenant_id: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "About":
        """Get information about this CodeGrade instance.

        :param health: Key required to view instance health information.
        :param tenant_id: The id of the tenant to get the site settings for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The about object for this instance.
        """

        url = "/api/v1/about"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, health)).if_just(
            lambda val: params.__setitem__("health", val)
        )
        maybe_from_nullable(t.cast(t.Any, tenant_id)).if_just(
            lambda val: params.__setitem__("tenant_id", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.about import About

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(About)
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
