"""The endpoints for group_set objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.create_group_group_set_data import CreateGroupGroupSetData
    from ..models.extended_group import ExtendedGroup
    from ..models.group_set import GroupSet


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class GroupSetService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def create_group(
        self: "GroupSetService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateGroupGroupSetData"],
        *,
        group_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedGroup":
        """Create a group for the given group set.

        :param json_body: The body of the request. See
            :class:`.CreateGroupGroupSetData` for information about the
            possible fields. You can provide this data as a
            :class:`.CreateGroupGroupSetData` or as a dictionary.
        :param group_set_id: The id of the group set where the new group should
            be placed in.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The newly created group.
        """

        url = "/api/v1/group_sets/{groupSetId}/group".format(
            groupSetId=group_set_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_group import ExtendedGroup

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedGroup)
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

    def get(
        self: "GroupSetService[codegrade.client.AuthenticatedClient]",
        *,
        group_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "GroupSet":
        """Get a single `GroupSet` by id.

        :param group_set_id: The id of the group set
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A response containing the JSON serialized group set.
        """

        url = "/api/v1/group_sets/{groupSetId}".format(groupSetId=group_set_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.group_set import GroupSet

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(GroupSet)
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

    def delete(
        self: "GroupSetService[codegrade.client.AuthenticatedClient]",
        *,
        group_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete a `GroupSet`.

        You can only delete a group set if there are no groups in the set and
        no assignment is connected to the group set.

        :param group_set_id: The id of the group set
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/group_sets/{groupSetId}".format(groupSetId=group_set_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 204):
            # fmt: off
            # fmt: on
            return parsers.ConstantlyParser(None).try_parse(resp)

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

    def get_all_groups(
        self: "GroupSetService[codegrade.client.AuthenticatedClient]",
        *,
        group_set_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedGroup]":
        """Get all groups for a given group set.

        :param group_set_id: The group set for which the groups should be
            returned.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All the groups for the given group set.
        """

        url = "/api/v1/group_sets/{groupSetId}/groups/".format(
            groupSetId=group_set_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_group import ExtendedGroup

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedGroup))
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
