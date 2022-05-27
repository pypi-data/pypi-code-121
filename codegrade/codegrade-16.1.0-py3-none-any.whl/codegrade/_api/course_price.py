"""The endpoints for course_price objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.coupon import Coupon
    from ..models.coupon_data_parser import CouponDataParser
    from ..models.coupon_usage import CouponUsage
    from ..models.pay_with_coupon_course_price_data import (
        PayWithCouponCoursePriceData,
    )
    from ..models.start_payment_course_price_data import (
        StartPaymentCoursePriceData,
    )
    from ..models.started_transaction import StartedTransaction


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class CoursePriceService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get_all_coupons(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        *,
        price_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "t.Sequence[Coupon]":
        """Get the coupons of a price.

        :param price_id: The price id for which you want to get all coupons.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The coupons (that the current user may see) of the price.
        """

        url = "/api/v1/course_prices/{priceId}/coupons/".format(
            priceId=price_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.coupon import CouponParser

            # fmt: on
            return parsers.JsonResponseParser(
                rqa.List(CouponParser)
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

    def create_coupon(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CouponDataParser"],
        *,
        price_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Coupon":
        """Create a new coupon for a course price.

        :param json_body: The body of the request. See
            :class:`.CouponDataParser` for information about the possible
            fields. You can provide this data as a :class:`.CouponDataParser`
            or as a dictionary.
        :param price_id: The price you want to create a coupon for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The coupon created for this course price.
        """

        url = "/api/v1/course_prices/{priceId}/coupons/".format(
            priceId=price_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.coupon import CouponParser

            # fmt: on
            return parsers.JsonResponseParser(CouponParser).try_parse(resp)

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

    def delete_coupon(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        *,
        price_id: "str",
        coupon_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "None":
        """Delete a coupon.

        :param price_id: The id of the price the coupon is connected to.
        :param coupon_id: The id of the coupon you want to delete.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing
        """

        url = "/api/v1/course_prices/{priceId}/coupons/{couponId}".format(
            priceId=price_id, couponId=coupon_id
        )
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

    def update_coupon(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "CouponDataParser"],
        *,
        price_id: "str",
        coupon_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Coupon":
        """Update the given coupon with new values.

        :param json_body: The body of the request. See
            :class:`.CouponDataParser` for information about the possible
            fields. You can provide this data as a :class:`.CouponDataParser`
            or as a dictionary.
        :param price_id: The price to which the coupon is connected.
        :param coupon_id: The id of the coupon you want to update.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The updated coupon
        """

        url = "/api/v1/course_prices/{priceId}/coupons/{couponId}".format(
            priceId=price_id, couponId=coupon_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.patch(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.coupon import CouponParser

            # fmt: on
            return parsers.JsonResponseParser(CouponParser).try_parse(resp)

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

    def start_payment(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "StartPaymentCoursePriceData"],
        *,
        price_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "StartedTransaction":
        """Create a new payment for the current user.

        :param json_body: The body of the request. See
            :class:`.StartPaymentCoursePriceData` for information about the
            possible fields. You can provide this data as a
            :class:`.StartPaymentCoursePriceData` or as a dictionary.
        :param price_id: The price you want to pay for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: A transaction for this course price with a `stripe_url` key
                  that can be used to pay. Be careful to check the state of the
                  transaction, as a payment might already be in progress.
        """

        url = "/api/v1/course_prices/{priceId}/pay".format(priceId=price_id)
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.put(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.started_transaction import StartedTransaction

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(StartedTransaction)
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

    def pay_with_coupon(
        self: "CoursePriceService[codegrade.client.AuthenticatedClient]",
        json_body: t.Union[dict, list, "PayWithCouponCoursePriceData"],
        *,
        price_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "CouponUsage":
        """Pay for a course with a coupon.

        :param json_body: The body of the request. See
            :class:`.PayWithCouponCoursePriceData` for information about the
            possible fields. You can provide this data as a
            :class:`.PayWithCouponCoursePriceData` or as a dictionary.
        :param price_id: The id of the price you want to pay for.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: Nothing
        """

        url = "/api/v1/course_prices/{priceId}/pay_with_coupon/".format(
            priceId=price_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(
                url=url, json=utils.to_dict(json_body), params=params
            )
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.coupon_usage import CouponUsage

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(CouponUsage)
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
