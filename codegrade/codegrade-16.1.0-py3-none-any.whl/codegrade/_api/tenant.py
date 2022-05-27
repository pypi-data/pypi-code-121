"""The endpoints for tenant objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.create_tenant_data import CreateTenantData
    from ..models.extended_course import ExtendedCourse
    from ..models.extended_tenant import ExtendedTenant
    from ..models.lti_provider_base import LTIProviderBase
    from ..models.partial_all_site_settings import PartialAllSiteSettings
    from ..models.patch_settings_tenant_data import PatchSettingsTenantData
    from ..models.patch_tenant_data import PatchTenantData
    from ..models.put_price_tenant_data import PutPriceTenantData
    from ..models.tenant_price import TenantPrice
    from ..models.tenant_statistics import TenantStatistics


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class TenantService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all(
        self,
        *,
        with_statistics: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedTenant]":
        """Get all tenants of an instance.

        :param with_statistics: Add statistics to returned tenants, if you have
            permission too see the statistics.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: All the tenants of this instance.
        """

        url = "/api/v1/tenants/"
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "with_statistics": utils.to_dict(with_statistics),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_tenant import ExtendedTenant

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedTenant))
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

    def create(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        multipart_data: t.Union[dict, list, "CreateTenantData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedTenant":
        """Create a new tenant.

        :param multipart_data: The data that should form the body of the
            request. See :class:`.CreateTenantData` for information about the
            possible fields.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The newly created tenant.
        """

        url = "/api/v1/tenants/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url,
                files=utils.to_multipart(utils.to_dict(multipart_data)),
                params=params,
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_tenant import ExtendedTenant

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedTenant)
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

    def put_price(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PutPriceTenantData"],
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "TenantPrice":
        """Update the price of the given course.

        :param json_body: The body of the request. See
            :class:`.PutPriceTenantData` for information about the possible
            fields. You can provide this data as a :class:`.PutPriceTenantData`
            or as a dictionary.
        :param tenant_id: The id of the tenant for which you want to update the
            price.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The created or updated price.
        """

        url = "/api/v1/tenants/{tenantId}/price".format(tenantId=tenant_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.tenant_price import TenantPrice

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(TenantPrice)
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

    def delete_price(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Update the price of the given course.

        :param tenant_id: The id of the tenant for which you want to delete the
            price.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing.
        """

        url = "/api/v1/tenants/{tenantId}/price".format(tenantId=tenant_id)
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

    def get(
        self,
        *,
        tenant_id: "str",
        with_statistics: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedTenant":
        """Get a tenant by id.

        :param tenant_id: The id of the tenant you want to retrieve.
        :param with_statistics: Add statistics to returned tenant, if you have
            permission too see the statistics.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The tenant with the given id.
        """

        url = "/api/v1/tenants/{tenantId}".format(tenantId=tenant_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "with_statistics": utils.to_dict(with_statistics),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_tenant import ExtendedTenant

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedTenant)
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
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchTenantData"],
        *,
        tenant_id: "str",
        with_statistics: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "ExtendedTenant":
        """Update a tenant by id.

        :param json_body: The body of the request. See
            :class:`.PatchTenantData` for information about the possible
            fields. You can provide this data as a :class:`.PatchTenantData` or
            as a dictionary.
        :param tenant_id: The id of the tenant you want to update.
        :param with_statistics: Add statistics to returned tenant, if you have
            permission too see the statistics.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated tenant.
        """

        url = "/api/v1/tenants/{tenantId}".format(tenantId=tenant_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "with_statistics": utils.to_dict(with_statistics),
        }

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_tenant import ExtendedTenant

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(ExtendedTenant)
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

    def get_courses(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[ExtendedCourse]":
        """Get the courses for this tenant.

        :param tenant_id: The tenant for which to get the courses.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The courses for this tenant.
        """

        url = "/api/v1/tenants/{tenantId}/courses/".format(tenantId=tenant_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.extended_course import ExtendedCourse

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(parsers.ParserFor.make(ExtendedCourse))
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

    def get_logo(
        self,
        *,
        tenant_id: "str",
        dark: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "bytes":
        """Get the logo of a tenant.

        :param tenant_id: The id of the tenant for which you want to get the
            logo.
        :param dark: If truhty the retrieved logo will be suited for the dark
            theme.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The logo of the tenant.
        """

        url = "/api/v1/tenants/{tenantId}/logo".format(tenantId=tenant_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "dark": utils.to_dict(dark),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            # fmt: on
            return parsers.ResponsePropertyParser("content", bytes).try_parse(
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

    def get_lti_providers(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[LTIProviderBase]":
        """List all LTI providers for this tenant.

        :param tenant_id: The id of the tenant to get the LTI providers for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of all known LTI providers.
        """

        url = "/api/v1/tenants/{tenantId}/lti_providers/".format(
            tenantId=tenant_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.lti_provider_base import LTIProviderBaseParser

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(LTIProviderBaseParser)
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

    def get_settings(
        self,
        *,
        tenant_id: "str",
        only_frontend: "bool" = False,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "PartialAllSiteSettings":
        """Get the settings for this tenant.

        :param tenant_id: The tenant for which to get the settings.
        :param only_frontend: Get only the frontend settings. When `True` the
            returned mapping will contain all frontend settings, even those
            that only have a global value.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The settings for this tenant.
        """

        url = "/api/v1/tenants/{tenantId}/settings/".format(tenantId=tenant_id)
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
            "only_frontend": utils.to_dict(only_frontend),
        }

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.partial_all_site_settings import (
                PartialAllSiteSettings,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(PartialAllSiteSettings)
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

    def patch_settings(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PatchSettingsTenantData"],
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "PartialAllSiteSettings":
        """Update the settings for this tenant.

        :param json_body: The body of the request. See
            :class:`.PatchSettingsTenantData` for information about the
            possible fields. You can provide this data as a
            :class:`.PatchSettingsTenantData` or as a dictionary.
        :param tenant_id: The tenant to update the settings for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated tenant settings.
        """

        url = "/api/v1/tenants/{tenantId}/settings/".format(tenantId=tenant_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.partial_all_site_settings import (
                PartialAllSiteSettings,
            )

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(PartialAllSiteSettings)
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

    def get_stats(
        self: "TenantService[codegrade.client.AuthenticatedClient]",
        *,
        tenant_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "TenantStatistics":
        """Get the statistics of a tenant.

        :param tenant_id: The id of the tenant for which you want to get the
            statistics.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The statistics of the specified tenant.
        """

        url = "/api/v1/tenants/{tenantId}/statistics/".format(
            tenantId=tenant_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.tenant_statistics import TenantStatistics

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(TenantStatistics)
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
