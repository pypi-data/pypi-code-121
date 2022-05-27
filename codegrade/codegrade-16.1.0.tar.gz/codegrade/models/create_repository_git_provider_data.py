"""The module that defines the ``CreateRepositoryGitProviderData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CreateRepositoryGitProviderData:
    """Input data required for the `Git Provider::CreateRepository` operation."""

    #: The name of the new repository
    name: "str"
    #: The assignment that should be connected to this repository
    assignment_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the new repository",
            ),
            rqa.RequiredArgument(
                "assignment_id",
                rqa.SimpleValue.int,
                doc=(
                    "The assignment that should be connected to this"
                    " repository"
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "assignment_id": to_dict(self.assignment_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateRepositoryGitProviderData"], d: t.Dict[str, t.Any]
    ) -> "CreateRepositoryGitProviderData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            assignment_id=parsed.assignment_id,
        )
        res.raw_data = d
        return res
