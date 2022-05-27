"""The module that defines the ``PatchRubricResultSubmissionData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..parsers import ParserFor, make_union
from ..utils import to_dict
from ._submission_rubric_item_data_parser import (
    _SubmissionRubricItemDataParser,
)


@dataclass
class PatchRubricResultSubmissionData_1:
    """ """

    #: An array of rubric ids to select. This format is deprecated.
    items: "t.Sequence[int]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "items",
                rqa.List(rqa.SimpleValue.int),
                doc=(
                    "An array of rubric ids to select. This format is"
                    " deprecated."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "items": to_dict(self.items),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchRubricResultSubmissionData_1"], d: t.Dict[str, t.Any]
    ) -> "PatchRubricResultSubmissionData_1":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            items=parsed.items,
        )
        res.raw_data = d
        return res


@dataclass
class PatchRubricResultSubmissionData_1_2:
    """ """

    #: An array of rubric items to select.
    items: "t.Sequence[_SubmissionRubricItemDataParser]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "items",
                rqa.List(
                    parsers.ParserFor.make(_SubmissionRubricItemDataParser)
                ),
                doc="An array of rubric items to select.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "items": to_dict(self.items),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchRubricResultSubmissionData_1_2"],
        d: t.Dict[str, t.Any],
    ) -> "PatchRubricResultSubmissionData_1_2":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            items=parsed.items,
        )
        res.raw_data = d
        return res


PatchRubricResultSubmissionData = t.Union[
    PatchRubricResultSubmissionData_1,
    PatchRubricResultSubmissionData_1_2,
]
PatchRubricResultSubmissionDataParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(PatchRubricResultSubmissionData_1),
        ParserFor.make(PatchRubricResultSubmissionData_1_2),
    ),
)
