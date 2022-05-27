"""The endpoints for notification objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.has_unread_notifcation_json import HasUnreadNotifcationJSON
    from ..models.notification import Notification
    from ..models.notifications_json import NotificationsJSON
    from ..models.patch_all_notification_data import PatchAllNotificationData
    from ..models.patch_notification_data import PatchNotificationData


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class NotificationService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self: "NotificationService[codegrade.client.AuthenticatedClient]",
        *,
        has_unread: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[NotificationsJSON, HasUnreadNotifcationJSON]":
        """Get all notifications for the current user.

        :param has_unread: If considered true a short digest will be sent, i.e.
            a single object with one key `has_unread` with a boolean value.
            Please use this if you simply want to check if there are unread
            notifications.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Either a list of notifications or a
                  `HasUnreadNotifcationJSON` based on the `has_unread` query
                  parameter.
        """

        url = "/api/v1/notifications/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "has_unread": utils.to_dict(has_unread),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.has_unread_notifcation_json import (
                HasUnreadNotifcationJSON,
            )
            from ..models.notifications_json import NotificationsJSON

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(NotificationsJSON),
                    parsers.ParserFor.make(HasUnreadNotifcationJSON),
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

    def patch_all(
        self: "NotificationService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchAllNotificationData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "NotificationsJSON":
        """Update the read status of multiple notifications.

        :param json_body: The body of the request. See
            :class:`.PatchAllNotificationData` for information about the
            possible fields. You can provide this data as a
            :class:`.PatchAllNotificationData` or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated notifications in the same order as given in the
                  body.
        """

        url = "/api/v1/notifications/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.notifications_json import NotificationsJSON

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(NotificationsJSON)
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

    def patch(
        self: "NotificationService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchNotificationData"],
        *,
        notification_id: "int",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Notification":
        """Update the read status for the given notification.

        :param json_body: The body of the request. See
            :class:`.PatchNotificationData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchNotificationData` or as a dictionary.
        :param notification_id: The id of the notification to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated notification.
        """

        url = "/api/v1/notifications/{notificationId}".format(
            notificationId=notification_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.notification import NotificationParser

            # fmt: on
            return parsers.JsonResponseParser(NotificationParser).try_parse(
                resp
            )

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
