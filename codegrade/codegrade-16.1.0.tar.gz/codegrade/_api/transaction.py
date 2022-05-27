"""The endpoints for transaction objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""
import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    import codegrade

    from ..models.transaction import Transaction


_ClientT = t.TypeVar("_ClientT", bound="codegrade.client._BaseClient")


class TransactionService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def get(
        self: "TransactionService[codegrade.client.AuthenticatedClient]",
        *,
        transaction_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Transaction":
        """Get a transaction by id.

        :param transaction_id: The id of the transaction you want to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The found transaction.
        """

        url = "/api/v1/transactions/{transactionId}".format(
            transactionId=transaction_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.transaction import Transaction

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Transaction)
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

    def refund(
        self: "TransactionService[codegrade.client.AuthenticatedClient]",
        *,
        transaction_id: "str",
        extra_parameters: t.Mapping[
            str, t.Union[str, bool, int, float]
        ] = None,
    ) -> "Transaction":
        """Refund a transaction.

        :param transaction_id: The id of the transaction you want to get.
        :param extra_parameters: The extra query parameters you might want to
            add. By default no extra query parameters are added.

        :returns: The found transaction.
        """

        url = "/api/v1/transactions/{transactionId}/refund".format(
            transactionId=transaction_id
        )
        params = extra_parameters or {}

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            # fmt: off
            from ..models.transaction import Transaction

            # fmt: on
            return parsers.JsonResponseParser(
                parsers.ParserFor.make(Transaction)
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
