"""The module that defines the ``ConnectRepositoryGitProviderData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class ConnectRepositoryGitProviderData:
    """Input data required for the `Git Provider::ConnectRepository` operation."""

    #: The assignment that should be connected to this repository
    assignment_id: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
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
            "assignment_id": to_dict(self.assignment_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ConnectRepositoryGitProviderData"], d: t.Dict[str, t.Any]
    ) -> "ConnectRepositoryGitProviderData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            assignment_id=parsed.assignment_id,
        )
        res.raw_data = d
        return res
