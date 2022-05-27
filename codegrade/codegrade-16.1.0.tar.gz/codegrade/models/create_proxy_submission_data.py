"""The module that defines the ``CreateProxySubmissionData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CreateProxySubmissionData:
    """Input data required for the `Submission::CreateProxy` operation."""

    #: Allow remote resources
    allow_remote_resources: "bool"
    #: Allow remote scripts
    allow_remote_scripts: "bool"
    #: Whether to show the teacher revision
    teacher_revision: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "allow_remote_resources",
                rqa.SimpleValue.bool,
                doc="Allow remote resources",
            ),
            rqa.RequiredArgument(
                "allow_remote_scripts",
                rqa.SimpleValue.bool,
                doc="Allow remote scripts",
            ),
            rqa.RequiredArgument(
                "teacher_revision",
                rqa.SimpleValue.bool,
                doc="Whether to show the teacher revision",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "allow_remote_resources": to_dict(self.allow_remote_resources),
            "allow_remote_scripts": to_dict(self.allow_remote_scripts),
            "teacher_revision": to_dict(self.teacher_revision),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateProxySubmissionData"], d: t.Dict[str, t.Any]
    ) -> "CreateProxySubmissionData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            allow_remote_resources=parsed.allow_remote_resources,
            allow_remote_scripts=parsed.allow_remote_scripts,
            teacher_revision=parsed.teacher_revision,
        )
        res.raw_data = d
        return res
