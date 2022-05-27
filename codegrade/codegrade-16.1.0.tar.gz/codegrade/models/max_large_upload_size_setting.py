"""The module that defines the ``MaxLargeUploadSizeSetting`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict


@dataclass
class MaxLargeUploadSizeSetting:
    """ """

    name: "t.Literal['MAX_LARGE_UPLOAD_SIZE']"
    value: "t.Optional[t.Union[int, str]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "name",
                rqa.StringEnum("MAX_LARGE_UPLOAD_SIZE"),
                doc="",
            ),
            rqa.RequiredArgument(
                "value",
                rqa.Nullable(
                    parsers.make_union(
                        rqa.SimpleValue.int, rqa.SimpleValue.str
                    )
                ),
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "value": to_dict(self.value),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["MaxLargeUploadSizeSetting"], d: t.Dict[str, t.Any]
    ) -> "MaxLargeUploadSizeSetting":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            value=parsed.value,
        )
        res.raw_data = d
        return res
