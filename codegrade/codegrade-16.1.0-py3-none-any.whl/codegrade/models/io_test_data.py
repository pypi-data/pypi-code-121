"""The module that defines the ``IOTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .io_test_base_data import IOTestBaseData


@dataclass
class IOTestData(IOTestBaseData):
    """The data of an IOTest."""

    #: Description template for sub-steps
    sub_description: Maybe["str"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: IOTestBaseData.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "sub_description",
                    rqa.SimpleValue.str,
                    doc="Description template for sub-steps",
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.sub_description = maybe_from_nullable(self.sub_description)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "program": to_dict(self.program),
            "inputs": to_dict(self.inputs),
        }
        if self.sub_description.is_just:
            res["sub_description"] = to_dict(self.sub_description.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IOTestData"], d: t.Dict[str, t.Any]
    ) -> "IOTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            program=parsed.program,
            inputs=parsed.inputs,
            sub_description=parsed.sub_description,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .io_test_input_case import IOTestInputCase

    # fmt: on
