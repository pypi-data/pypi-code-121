"""The module that defines the ``Option`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class Option:
    """A site setting of CodeGrade."""

    #: The name of the option.
    name: "str"
    #: The default value of the option.
    default: "t.Any"
    #: The current value of the option.
    value: "t.Any"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the option.",
            ),
            rqa.RequiredArgument(
                "default",
                rqa.AnyValue,
                doc="The default value of the option.",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.AnyValue,
                doc="The current value of the option.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "default": to_dict(self.default),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["Option"], d: t.Dict[str, t.Any]) -> "Option":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            default=parsed.default,
            value=parsed.value,
        )
        res.raw_data = d
        return res
