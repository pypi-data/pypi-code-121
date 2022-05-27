"""The module that defines the ``PatchSubmitTypesAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .json_patch_submit_types_assignment import JsonPatchSubmitTypesAssignment
from .types import File


@dataclass
class PatchSubmitTypesAssignmentData:
    """Input data required for the `Assignment::PatchSubmitTypes` operation."""

    json: "JsonPatchSubmitTypesAssignment"
    template: Maybe["t.Sequence[File]"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "json",
                parsers.ParserFor.make(JsonPatchSubmitTypesAssignment),
                doc="",
            ),
            rqa.OptionalArgument(
                "template",
                rqa.List(rqa.AnyValue),
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.template = maybe_from_nullable(self.template)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "json": to_dict(self.json),
        }
        if self.template.is_just:
            res["template"] = to_dict(self.template.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["PatchSubmitTypesAssignmentData"], d: t.Dict[str, t.Any]
    ) -> "PatchSubmitTypesAssignmentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            json=parsed.json,
            template=parsed.template,
        )
        res.raw_data = d
        return res
