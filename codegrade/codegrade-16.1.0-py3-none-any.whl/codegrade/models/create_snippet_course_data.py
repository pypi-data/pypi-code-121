"""The module that defines the ``CreateSnippetCourseData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CreateSnippetCourseData:
    """Input data required for the `Course::CreateSnippet` operation."""

    #: The key of the new snippet
    key: "str"
    #: The value of the new snippet
    value: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "key",
                rqa.SimpleValue.str,
                doc="The key of the new snippet",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.SimpleValue.str,
                doc="The value of the new snippet",
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
        cls: t.Type["CreateSnippetCourseData"], d: t.Dict[str, t.Any]
    ) -> "CreateSnippetCourseData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            key=parsed.key,
            value=parsed.value,
        )
        res.raw_data = d
        return res
