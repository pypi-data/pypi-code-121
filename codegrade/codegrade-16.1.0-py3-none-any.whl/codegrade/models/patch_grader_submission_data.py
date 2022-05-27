"""The module that defines the ``PatchGraderSubmissionData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class PatchGraderSubmissionData:
    """Input data required for the `Submission::PatchGrader` operation."""

    #: Id of the new grader.
    user_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "user_id",
                rqa.SimpleValue.int,
                doc="Id of the new grader.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "user_id": to_dict(self.user_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchGraderSubmissionData"], d: t.Dict[str, t.Any]
    ) -> "PatchGraderSubmissionData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            user_id=parsed.user_id,
        )
        res.raw_data = d
        return res
