"""The module that defines the ``CourseRegistrationLink`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_role import CourseRole


@dataclass
class CourseRegistrationLink:
    """The JSON representation of a course registration link."""

    #: The id of this link
    id: "str"
    #: The moment this link will stop working
    expiration_date: "datetime.datetime"
    #: The role new users will get
    role: "CourseRole"
    #: Can users register with this link
    allow_register: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of this link",
            ),
            rqa.RequiredArgument(
                "expiration_date",
                rqa.RichValue.DateTime,
                doc="The moment this link will stop working",
            ),
            rqa.RequiredArgument(
                "role",
                parsers.ParserFor.make(CourseRole),
                doc="The role new users will get",
            ),
            rqa.RequiredArgument(
                "allow_register",
                rqa.SimpleValue.bool,
                doc="Can users register with this link",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "expiration_date": to_dict(self.expiration_date),
            "role": to_dict(self.role),
            "allow_register": to_dict(self.allow_register),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseRegistrationLink"], d: t.Dict[str, t.Any]
    ) -> "CourseRegistrationLink":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            expiration_date=parsed.expiration_date,
            role=parsed.role,
            allow_register=parsed.allow_register,
        )
        res.raw_data = d
        return res
