"""The module that defines the ``UpgradedLTIProviderException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from ..utils import to_dict
from .base_error import BaseError


@dataclass
class UpgradedLTIProviderException(BaseError):
    """The exception raised when a LTI 1.1 provider has been upgraded to a LTI
    1.3 provider an therefore cannot be used anymore.
    """

    #: The id of the provider this provider was upgraded to.
    upgraded_lti1p3_id: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "upgraded_lti1p3_id",
                    rqa.SimpleValue.str,
                    doc=(
                        "The id of the provider this provider was upgraded to."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "upgraded_lti1p3_id": to_dict(self.upgraded_lti1p3_id),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UpgradedLTIProviderException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "UpgradedLTIProviderException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            upgraded_lti1p3_id=parsed.upgraded_lti1p3_id,
            message=parsed.message,
            description=parsed.description,
            code=parsed.code,
            request_id=parsed.request_id,
            response=response,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .api_codes import APICodes

    # fmt: on
