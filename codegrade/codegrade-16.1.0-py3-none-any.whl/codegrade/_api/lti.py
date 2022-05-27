"""The endpoints for lti objects.

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

    from ..models.create_lti_data import CreateLTIData
    from ..models.lti1p1_provider import LTI1p1Provider
    from ..models.lti1p3_provider import LTI1p3Provider
    from ..models.lti_provider_base import LTIProviderBase
    from ..models.patch1_p1_provider_lti_data import Patch1P1ProviderLTIData
    from ..models.patch1_p3_provider_lti_data import Patch1P3ProviderLTIData


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class LTIService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def create(
        self: "LTIService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CreateLTIData"],
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "LTIProviderBase":
        """Create a new LTI 1.1 or 1.3 provider.

        This route is part of the public API.

        :param json_body: The body of the request. See :class:`.CreateLTIData`
            for information about the possible fields. You can provide this
            data as a :class:`.CreateLTIData` or as a dictionary.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The just created provider.
        """

        url = "/api/v1/lti1.3/providers/"
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.lti_provider_base import LTIProviderBaseParser

            # fmt: on
            return parsers.JsonResponseParser(LTIProviderBaseParser).try_parse(
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

    def patch_1p1_provider(
        self,
        json_body: t.Union[dict, list, "Patch1P1ProviderLTIData"],
        *,
        lti_provider_id: "str",
        secret: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "LTI1p1Provider":
        """Update the given LTI 1.1 provider.

        This route is part of the public api.

        :param json_body: The body of the request. See
            :class:`.Patch1P1ProviderLTIData` for information about the
            possible fields. You can provide this data as a
            :class:`.Patch1P1ProviderLTIData` or as a dictionary.
        :param lti_provider_id: The id of the provider you want to update.
        :param secret: The secret to use to update the provider.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated provider.
        """

        url = "/api/v1/lti1.1/providers/{ltiProviderId}".format(
            ltiProviderId=lti_provider_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, secret)).if_just(
            lambda val: params.__setitem__("secret", val)
        )

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.lti1p1_provider import LTI1p1ProviderParser

            # fmt: on
            return parsers.JsonResponseParser(LTI1p1ProviderParser).try_parse(
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

    def get(
        self,
        *,
        lti_provider_id: "str",
        secret: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "LTIProviderBase":
        """Get a LTI provider.

        This route is part of the public API.

        :param lti_provider_id: The id of the provider you want to get.
        :param secret: The secret to use to update the provider.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The requested LTI 1.1 or 1.3 provider.
        """

        url = "/api/v1/lti/providers/{ltiProviderId}".format(
            ltiProviderId=lti_provider_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, secret)).if_just(
            lambda val: params.__setitem__("secret", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.lti_provider_base import LTIProviderBaseParser

            # fmt: on
            return parsers.JsonResponseParser(LTIProviderBaseParser).try_parse(
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

    def get_all(
        self: "LTIService[codegrade.client.AuthenticatedClient]",
        *,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[LTIProviderBase]":
        """List all known LTI providers for this instance.

        This route is part of the public API.

        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A list of all known LTI providers.
        """

        url = "/api/v1/lti/providers/"
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

    def patch_1p3_provider(
        self,
        json_body: t.Union[dict, list, "Patch1P3ProviderLTIData"],
        *,
        lti_provider_id: "str",
        secret: Maybe["str"] = Nothing,
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "LTI1p3Provider":
        """Update the given LTI 1.3 provider.

        This route is part of the public API.

        :param json_body: The body of the request. See
            :class:`.Patch1P3ProviderLTIData` for information about the
            possible fields. You can provide this data as a
            :class:`.Patch1P3ProviderLTIData` or as a dictionary.
        :param lti_provider_id: The id of the provider you want to update.
        :param secret: The secret to use to update the provider.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated LTI 1.3 provider.
        """

        url = "/api/v1/lti1.3/providers/{ltiProviderId}".format(
            ltiProviderId=lti_provider_id
        )
        params: t.Dict[str, t.Any] = {
            **(extra_parameters or {}),
        }
        maybe_from_nullable(t.cast(t.Any, secret)).if_just(
            lambda val: params.__setitem__("secret", val)
        )

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.lti1p3_provider import LTI1p3ProviderParser

            # fmt: on
            return parsers.JsonResponseParser(LTI1p3ProviderParser).try_parse(
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
