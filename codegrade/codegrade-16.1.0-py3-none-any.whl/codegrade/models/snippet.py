"""The module that defines the ``Snippet`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class Snippet:
    """This class defines a personal snippet."""

    #: The id of the snippet.
    id: "int"
    #: The key under which the snippet was saved.
    key: "str"
    #: The value of the snippet.
    value: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the snippet.",
            ),
            rqa.RequiredArgument(
                "key",
                rqa.SimpleValue.str,
                doc="The key under which the snippet was saved.",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.SimpleValue.str,
                doc="The value of the snippet.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "key": to_dict(self.key),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["Snippet"], d: t.Dict[str, t.Any]) -> "Snippet":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            key=parsed.key,
            value=parsed.value,
        )
        res.raw_data = d
        return res
