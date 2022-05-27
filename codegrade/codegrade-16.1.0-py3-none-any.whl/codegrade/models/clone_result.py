"""The module that defines the ``CloneResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .work import Work


@dataclass
class CloneResult:
    """The data returned after a successful clone."""

    #: The work that was created.
    work: "Work"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "work",
                parsers.ParserFor.make(Work),
                doc="The work that was created.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "work": to_dict(self.work),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CloneResult"], d: t.Dict[str, t.Any]
    ) -> "CloneResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            work=parsed.work,
        )
        res.raw_data = d
        return res
