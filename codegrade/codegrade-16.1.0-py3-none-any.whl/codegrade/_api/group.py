"""The endpoints for group objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.extended_group import ExtendedGroup
    from ..models.rename_group_group_data import RenameGroupGroupData
    from ..models.user_input import UserInput


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class GroupService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def add_member(
        self: "GroupService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "UserInput"],
        *,
        group_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedGroup":
        """Add a user (member) to a group.

        :param json_body: The body of the request. See :class:`.UserInput` for
            information about the possible fields. You can provide this data as
            a :class:`.UserInput` or as a dictionary.
        :param group_id: The id of the group the user should be added to.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The group with the newly added user.
        """

        url = "/api/v1/groups/{groupId}/member".format(groupId=group_id)
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
        self: "GroupService[codegrade.client.AuthenticatedClient]",
        *,
        group_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedGroup":
        """Get a group by id.

        :param group_id: The id of the group to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested group.
        """

        url = "/api/v1/groups/{groupId}".format(groupId=group_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
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

    def delete(
        self: "GroupService[codegrade.client.AuthenticatedClient]",
        *,
        group_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete a group by id.

        This action is irreversible!

        This is only possible if the group doesn't have any submissions
        associated with it.

        :param group_id: The id of the group to delete.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/groups/{groupId}".format(groupId=group_id)
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

    def remove_member(
        self: "GroupService[codegrade.client.AuthenticatedClient]",
        *,
        group_id: "int",
        user_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedGroup":
        """Remove a member from a group.

        If the group has a submission you cannot delete the last remaining
        member of a group.

        :param group_id: The group the user should be removed from.
        :param user_id: The user that should be removed.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The group without the removed user.
        """

        url = "/api/v1/groups/{groupId}/members/{userId}".format(
            groupId=group_id, userId=user_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.delete(url=url, params=params)
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

    def rename_group(
        self: "GroupService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "RenameGroupGroupData"],
        *,
        group_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedGroup":
        """Update the name of the group.

        :param json_body: The body of the request. See
            :class:`.RenameGroupGroupData` for information about the possible
            fields. You can provide this data as a
            :class:`.RenameGroupGroupData` or as a dictionary.
        :param group_id: The id of the group that should be updated.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The group with the updated name.
        """

        url = "/api/v1/groups/{groupId}/name".format(groupId=group_id)
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
