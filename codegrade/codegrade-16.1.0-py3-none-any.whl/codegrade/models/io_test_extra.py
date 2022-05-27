"""The module that defines the ``IOTestExtra`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .io_test_data import IOTestData


@dataclass
class IOTestExtra:
    """The extra data for an IOTest."""

    #: This is an IO Test.
    type: "t.Literal['io_test']"
    #: The data for this IO test.
    data: "IOTestData"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("io_test"),
                doc="This is an IO Test.",
            ),
            rqa.RequiredArgument(
                "data",
                parsers.ParserFor.make(IOTestData),
                doc="The data for this IO test.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "data": to_dict(self.data),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestExtra"], d: t.Dict[str, t.Any]
    ) -> "IOTestExtra":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            data=parsed.data,
        )
        res.raw_data = d
        return res
