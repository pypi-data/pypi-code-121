"""The module that defines the ``PostOAuthTokenData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PostOAuthTokenData:
    """Input data required for the `OAuth Token::Post` operation."""

    #: The provider for which you want to create a token.
    provider_id: "str"
    #: A temporary id that can be used to get the token once it has been
    #: created.
    temp_id: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "provider_id",
                rqa.SimpleValue.str,
                doc="The provider for which you want to create a token.",
            ),
            rqa.RequiredArgument(
                "temp_id",
                rqa.SimpleValue.str,
                doc=(
                    "A temporary id that can be used to get the token once it"
                    " has been created."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "provider_id": to_dict(self.provider_id),
            "temp_id": to_dict(self.temp_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PostOAuthTokenData"], d: t.Dict[str, t.Any]
    ) -> "PostOAuthTokenData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            provider_id=parsed.provider_id,
            temp_id=parsed.temp_id,
        )
        res.raw_data = d
        return res
