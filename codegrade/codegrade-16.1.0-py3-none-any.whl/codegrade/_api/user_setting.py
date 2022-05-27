"""The endpoints for user_setting objects.

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

    from ..models.non_present_preference import NonPresentPreference
    from ..models.notification_setting import NotificationSetting
    from ..models.patch_notification_setting_user_setting_data import (
        PatchNotificationSettingUserSettingData,
    )
    from ..models.patch_ui_preference_user_setting_data import (
        PatchUiPreferenceUserSettingData,
    )
    from ..models.present_preference import PresentPreference


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class UserSettingService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all_notification_settings(
        self,
        *,
        token: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "NotificationSetting":
        """Update preferences for notifications.

        :param token: The token with which you want to get the preferences, if
            not given the preferences are retrieved for the currently logged in
            user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The preferences for the user as described by the `token`.
        """

        url = "/api/v1/settings/notification_settings/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, token)).if_just(
            lambda val: params.__setitem__("token", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.notification_setting import NotificationSetting

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(NotificationSetting)
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

    def patch_notification_setting(
        self,
        json_body: t.Union[
            dict, list, "PatchNotificationSettingUserSettingData"
        ],
        *,
        token: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Update preferences for notifications.

        :param json_body: The body of the request. See
            :class:`.PatchNotificationSettingUserSettingData` for information
            about the possible fields. You can provide this data as a
            :class:`.PatchNotificationSettingUserSettingData` or as a
            dictionary.
        :param token: The token with which you want to update the preferences,
            if not given the preferences are updated for the currently logged
            in user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/settings/notification_settings/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, token)).if_just(
            lambda val: params.__setitem__("token", val)
        )

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
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

    def get_ui_preference(
        self,
        *,
        name: Maybe["str"] = Nothing,
        token: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[PresentPreference, NonPresentPreference, t.Mapping[str, t.Any]]":
        """Get ui preferences.

        :param name: The preference name you want to get.
        :param token: The token with which you want to get the preferences, if
            not given the preferences are retrieved for the currently logged in
            user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The preferences for the user as described by the `token`.
        """

        url = "/api/v1/settings/ui_preferences/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, name)).if_just(
            lambda val: params.__setitem__("name", val)
        )
        maybe_from_nullable(t.cast(t.Any, token)).if_just(
            lambda val: params.__setitem__("token", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.non_present_preference import NonPresentPreference
            from ..models.present_preference import PresentPreference

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(PresentPreference),
                    parsers.ParserFor.make(NonPresentPreference),
                    rqa.LookupMapping(rqa.AnyValue),
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

    def patch_ui_preference(
        self,
        json_body: t.Union[dict, list, "PatchUiPreferenceUserSettingData"],
        *,
        token: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Update ui preferences.

        :param json_body: The body of the request. See
            :class:`.PatchUiPreferenceUserSettingData` for information about
            the possible fields. You can provide this data as a
            :class:`.PatchUiPreferenceUserSettingData` or as a dictionary.
        :param token: The token with which you want to update the preferences,
            if not given the preferences are updated for the currently logged
            in user.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/settings/ui_preferences/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, token)).if_just(
            lambda val: params.__setitem__("token", val)
        )

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
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
