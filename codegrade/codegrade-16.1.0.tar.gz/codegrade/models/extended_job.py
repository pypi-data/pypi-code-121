"""The module that defines the ``ExtendedJob`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .job import Job


@dataclass
class ExtendedJob(Job):
    """The extended JSON serialization of a job."""

    #: The name of the job.
    name: "str"
    #: The kwargs given to the job.
    kwargs: "t.Mapping[str, t.Any]"
    #: The current try of the job.
    try_n: "int"
    #: The time the job should be executed.
    eta: "datetime.datetime"
    #: Possibly the traceback of the job. Only not `null` when the job failed.
    traceback: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: Job.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "name",
                    rqa.SimpleValue.str,
                    doc="The name of the job.",
                ),
                rqa.RequiredArgument(
                    "kwargs",
                    rqa.LookupMapping(rqa.AnyValue),
                    doc="The kwargs given to the job.",
                ),
                rqa.RequiredArgument(
                    "try_n",
                    rqa.SimpleValue.int,
                    doc="The current try of the job.",
                ),
                rqa.RequiredArgument(
                    "eta",
                    rqa.RichValue.DateTime,
                    doc="The time the job should be executed.",
                ),
                rqa.RequiredArgument(
                    "traceback",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc=(
                        "Possibly the traceback of the job. Only not `null`"
                        " when the job failed."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "name": to_dict(self.name),
            "kwargs": to_dict(self.kwargs),
            "try_n": to_dict(self.try_n),
            "eta": to_dict(self.eta),
            "traceback": to_dict(self.traceback),
            "id": to_dict(self.id),
            "state": to_dict(self.state),
            "result": to_dict(self.result),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtendedJob"], d: t.Dict[str, t.Any]
    ) -> "ExtendedJob":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            name=parsed.name,
            kwargs=parsed.kwargs,
            try_n=parsed.try_n,
            eta=parsed.eta,
            traceback=parsed.traceback,
            id=parsed.id,
            state=parsed.state,
            result=parsed.result,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .task_result_state import TaskResultState

    # fmt: on
