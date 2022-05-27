"""The module that defines the ``HealthInformation`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class HealthInformation:
    """Information about the health of this instance."""

    #: Always true.
    application: "bool"
    #: Is the database ok?
    database: "bool"
    #: Is the upload storage system ok?
    uploads: "bool"
    #: Can the broker be reached?
    broker: "bool"
    #: Is the mirror upload storage system ok?
    mirror_uploads: "bool"
    #: Is the temporary directory on this server ok?
    temp_dir: "bool"
    #: Are the tasks ok?
    tasks: "bool"
    #: Is AutoTest running A-OK?
    auto_test: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "application",
                rqa.SimpleValue.bool,
                doc="Always true.",
            ),
            rqa.RequiredArgument(
                "database",
                rqa.SimpleValue.bool,
                doc="Is the database ok?",
            ),
            rqa.RequiredArgument(
                "uploads",
                rqa.SimpleValue.bool,
                doc="Is the upload storage system ok?",
            ),
            rqa.RequiredArgument(
                "broker",
                rqa.SimpleValue.bool,
                doc="Can the broker be reached?",
            ),
            rqa.RequiredArgument(
                "mirror_uploads",
                rqa.SimpleValue.bool,
                doc="Is the mirror upload storage system ok?",
            ),
            rqa.RequiredArgument(
                "temp_dir",
                rqa.SimpleValue.bool,
                doc="Is the temporary directory on this server ok?",
            ),
            rqa.RequiredArgument(
                "tasks",
                rqa.SimpleValue.bool,
                doc="Are the tasks ok?",
            ),
            rqa.RequiredArgument(
                "auto_test",
                rqa.SimpleValue.bool,
                doc="Is AutoTest running A-OK?",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "application": to_dict(self.application),
            "database": to_dict(self.database),
            "uploads": to_dict(self.uploads),
            "broker": to_dict(self.broker),
            "mirror_uploads": to_dict(self.mirror_uploads),
            "temp_dir": to_dict(self.temp_dir),
            "tasks": to_dict(self.tasks),
            "auto_test": to_dict(self.auto_test),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["HealthInformation"], d: t.Dict[str, t.Any]
    ) -> "HealthInformation":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            application=parsed.application,
            database=parsed.database,
            uploads=parsed.uploads,
            broker=parsed.broker,
            mirror_uploads=parsed.mirror_uploads,
            temp_dir=parsed.temp_dir,
            tasks=parsed.tasks,
            auto_test=parsed.auto_test,
        )
        res.raw_data = d
        return res
