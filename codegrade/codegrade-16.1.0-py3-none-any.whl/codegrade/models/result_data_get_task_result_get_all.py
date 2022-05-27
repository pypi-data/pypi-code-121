"""The module that defines the ``ResultDataGetTaskResultGetAll`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .extended_job import ExtendedJob


@dataclass
class ResultDataGetTaskResultGetAll:
    """The history of jobs for an instance."""

    #: Jobs that have not yet started
    not_started: "t.Sequence[ExtendedJob]"
    #: Jobs that are currently running.
    active: "t.Sequence[ExtendedJob]"
    #: A part of the jobs that have finished.
    finished: "t.Sequence[ExtendedJob]"
    #: The total amount of jobs that have finished.
    total_finished: "int"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "not_started",
                rqa.List(parsers.ParserFor.make(ExtendedJob)),
                doc="Jobs that have not yet started",
            ),
            rqa.RequiredArgument(
                "active",
                rqa.List(parsers.ParserFor.make(ExtendedJob)),
                doc="Jobs that are currently running.",
            ),
            rqa.RequiredArgument(
                "finished",
                rqa.List(parsers.ParserFor.make(ExtendedJob)),
                doc="A part of the jobs that have finished.",
            ),
            rqa.RequiredArgument(
                "total_finished",
                rqa.SimpleValue.int,
                doc="The total amount of jobs that have finished.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "not_started": to_dict(self.not_started),
            "active": to_dict(self.active),
            "finished": to_dict(self.finished),
            "total_finished": to_dict(self.total_finished),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ResultDataGetTaskResultGetAll"], d: t.Dict[str, t.Any]
    ) -> "ResultDataGetTaskResultGetAll":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            not_started=parsed.not_started,
            active=parsed.active,
            finished=parsed.finished,
            total_finished=parsed.total_finished,
        )
        res.raw_data = d
        return res
