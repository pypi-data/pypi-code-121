"""The module that defines the ``AllAutoTestResults`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .auto_test_result_with_extra_data import AutoTestResultWithExtraData


@dataclass
class AllAutoTestResults:
    """The result when requesting all non started AutoTest results."""

    #: The total amount of not started AutoTest results
    total_amount: "int"
    #: The request results, these are limited by the given query parameters.
    results: "t.Sequence[AutoTestResultWithExtraData]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "total_amount",
                rqa.SimpleValue.int,
                doc="The total amount of not started AutoTest results",
            ),
            rqa.RequiredArgument(
                "results",
                rqa.List(parsers.ParserFor.make(AutoTestResultWithExtraData)),
                doc=(
                    "The request results, these are limited by the given query"
                    " parameters."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "total_amount": to_dict(self.total_amount),
            "results": to_dict(self.results),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AllAutoTestResults"], d: t.Dict[str, t.Any]
    ) -> "AllAutoTestResults":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            total_amount=parsed.total_amount,
            results=parsed.results,
        )
        res.raw_data = d
        return res
