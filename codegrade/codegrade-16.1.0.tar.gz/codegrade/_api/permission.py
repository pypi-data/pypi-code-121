"""The endpoints for permission objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.course_perm_map import CoursePermMap
    from ..models.global_perm_map import GlobalPermMap


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class PermissionService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self: "PermissionService[codegrade.client.AuthenticatedClient]",
        *,
        type: "t.Literal['course', 'global']",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[t.Mapping[str, CoursePermMap], GlobalPermMap]":
        """Get all the global permissions or all course permissions for all
        courses for the currently logged in user.

        :param type: The type of permissions to get. This can be `global` or
            `course`. If `course` is passed this will return the permissions as
            if you have already paid, even if this is not the case.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The returning object depends on the given `type`. If it was
                  `global` a mapping between permissions name and a boolean
                  indicating if the currently logged in user has this
                  permissions is returned. If it was `course` such a mapping is
                  returned for every course the user is enrolled in. So it is a
                  mapping between course ids and permission mapping.
        """

        url = "/api/v1/permissions/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "type": utils.to_dict(type),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.course_perm_map import CoursePermMap
            from ..models.global_perm_map import GlobalPermMap

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    rqa.LookupMapping(parsers.ParserFor.make(CoursePermMap)),
                    parsers.ParserFor.make(GlobalPermMap),
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
