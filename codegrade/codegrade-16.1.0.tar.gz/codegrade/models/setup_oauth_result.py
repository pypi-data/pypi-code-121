"""The module that defines the ``SetupOAuthResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class SetupOAuthResult:
    """Data returned when putting an OAuth token while the connection does not
    yet exist.
    """

    #: The URL the user should open.
    return_url: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "return_url",
                rqa.SimpleValue.str,
                doc="The URL the user should open.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "return_url": to_dict(self.return_url),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["SetupOAuthResult"], d: t.Dict[str, t.Any]
    ) -> "SetupOAuthResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            return_url=parsed.return_url,
        )
        res.raw_data = d
        return res
