"""The module that defines the ``CourseOfCoursePrice`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CourseOfCoursePrice:
    """The data you will receive for a course of a course price."""

    #: The id of the course that is connected to this price.
    id: "int"
    #: The id of the tenant of the course connected to this price.
    tenant_id: "t.Optional[str]"
    #: The name of the course that is connected to this price.
    name: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the course that is connected to this price.",
            ),
            rqa.RequiredArgument(
                "tenant_id",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The id of the tenant of the course connected to this"
                    " price."
                ),
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the course that is connected to this price.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "tenant_id": to_dict(self.tenant_id),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseOfCoursePrice"], d: t.Dict[str, t.Any]
    ) -> "CourseOfCoursePrice":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            tenant_id=parsed.tenant_id,
            name=parsed.name,
        )
        res.raw_data = d
        return res
