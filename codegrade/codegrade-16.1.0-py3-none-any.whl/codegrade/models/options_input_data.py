"""The module that defines the ``OptionsInputData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class OptionsInputData:
    """The input data for a single option for the SubmissionValidator."""

    #: What option is this.
    key: "t.Literal['allow_override', 'delete_empty_directories', 'remove_leading_directories']"
    #: Is this option enabled.
    value: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "key",
                rqa.StringEnum(
                    "allow_override",
                    "delete_empty_directories",
                    "remove_leading_directories",
                ),
                doc="What option is this.",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.SimpleValue.bool,
                doc="Is this option enabled.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "key": to_dict(self.key),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["OptionsInputData"], d: t.Dict[str, t.Any]
    ) -> "OptionsInputData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            key=parsed.key,
            value=parsed.value,
        )
        res.raw_data = d
        return res
