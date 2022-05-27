"""The module that defines the ``UploadSubmissionAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict
from .types import File


@dataclass
class UploadSubmissionAssignmentData:
    """Input data required for the `Assignment::UploadSubmission` operation."""

    file: Maybe["t.Sequence[File]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "file",
                rqa.List(rqa.AnyValue),
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.file = maybe_from_nullable(self.file)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.file.is_just:
            res["file"] = to_dict(self.file.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UploadSubmissionAssignmentData"], d: t.Dict[str, t.Any]
    ) -> "UploadSubmissionAssignmentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            file=parsed.file,
        )
        res.raw_data = d
        return res
