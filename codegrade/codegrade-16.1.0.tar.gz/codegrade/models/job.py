"""The module that defines the ``Job`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .task_result_state import TaskResultState


@dataclass
class Job:
    """A job as JSON."""

    #: The id of the job. Can be used to revoke and/or restart it.
    id: "str"
    #: The state of the job.
    state: "TaskResultState"
    #: Possibly the result of the job.
    result: "t.Optional[t.Any]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc=(
                    "The id of the job. Can be used to revoke and/or"
                    " restart it."
                ),
            ),
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(TaskResultState),
                doc="The state of the job.",
            ),
            rqa.RequiredArgument(
                "result",
                rqa.Nullable(rqa.AnyValue),
                doc="Possibly the result of the job.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "state": to_dict(self.state),
            "result": to_dict(self.result),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["Job"], d: t.Dict[str, t.Any]) -> "Job":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            state=parsed.state,
            result=parsed.result,
        )
        res.raw_data = d
        return res
