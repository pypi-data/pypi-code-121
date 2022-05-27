"""The module that defines the ``CreateAutoTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .json_create_auto_test import JsonCreateAutoTest
from .types import File


@dataclass
class CreateAutoTestData:
    """Input data required for the `AutoTest::Create` operation."""

    json: "JsonCreateAutoTest"
    fixture: Maybe["t.Sequence[File]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "json",
                parsers.ParserFor.make(JsonCreateAutoTest),
                doc="",
            ),
            rqa.OptionalArgument(
                "fixture",
                rqa.List(rqa.AnyValue),
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.fixture = maybe_from_nullable(self.fixture)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "json": to_dict(self.json),
        }
        if self.fixture.is_just:
            res["fixture"] = to_dict(self.fixture.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateAutoTestData"], d: t.Dict[str, t.Any]
    ) -> "CreateAutoTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            json=parsed.json,
            fixture=parsed.fixture,
        )
        res.raw_data = d
        return res
