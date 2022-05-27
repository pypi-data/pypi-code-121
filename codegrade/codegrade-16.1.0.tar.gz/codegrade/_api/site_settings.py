"""The endpoints for site_settings objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.all_site_settings import AllSiteSettings
    from ..models.frontend_site_settings import FrontendSiteSettings
    from ..models.patch_site_settings_data import PatchSiteSettingsData


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class SiteSettingsService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self,
        *,
        only_frontend: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Union[AllSiteSettings, FrontendSiteSettings]":
        """Get the settings for this CodeGrade instance.

        :param only_frontend: Get only the frontend settings.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The site settings for this instance.
        """

        url = "/api/v1/site_settings/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "only_frontend": utils.to_dict(only_frontend),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.all_site_settings import AllSiteSettings
            from ..models.frontend_site_settings import FrontendSiteSettings

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.make_union(
                    parsers.ParserFor.make(AllSiteSettings),
                    parsers.ParserFor.make(FrontendSiteSettings),
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

    def patch(
        self: "SiteSettingsService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchSiteSettingsData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "AllSiteSettings":
        """Update the settings for this CodeGrade instance.

        :param json_body: The body of the request. See
            :class:`.PatchSiteSettingsData` for information about the possible
            fields. You can provide this data as a
            :class:`.PatchSiteSettingsData` or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated site settings.
        """

        url = "/api/v1/site_settings/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.all_site_settings import AllSiteSettings

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(AllSiteSettings)
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
