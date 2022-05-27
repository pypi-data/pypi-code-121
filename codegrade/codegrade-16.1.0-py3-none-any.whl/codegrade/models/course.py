"""The module that defines the ``Course`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_price import CoursePrice
from .course_state import CourseState
from .lti_provider_base import LTIProviderBase, LTIProviderBaseParser


@dataclass
class Course:
    """The way this class will be represented in JSON."""

    #: The id of this course
    id: "int"
    #: The name of this course
    name: "str"
    #: The date this course was created
    created_at: "datetime.datetime"
    #: Is this a virtual course.
    virtual: "bool"
    #: The lti provider that manages this course, if `null` this is not a LTI
    #: course.
    lti_provider: "t.Optional[LTIProviderBase]"
    #: The state this course is in.
    state: "CourseState"
    #: The id of the tenant that owns this course.
    tenant_id: "t.Optional[str]"
    #: Is the lock date feature enabled for this course. This will be `True`
    #: for every course created after the release of version N.2.
    copy_lock_date: "bool"
    #: The price of this course.
    price: "t.Optional[CoursePrice]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this course",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of this course",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="The date this course was created",
            ),
            rqa.RequiredArgument(
                "virtual",
                rqa.SimpleValue.bool,
                doc="Is this a virtual course.",
            ),
            rqa.RequiredArgument(
                "lti_provider",
                rqa.Nullable(LTIProviderBaseParser),
                doc=(
                    "The lti provider that manages this course, if `null` this"
                    " is not a LTI course."
                ),
            ),
            rqa.RequiredArgument(
                "state",
                rqa.EnumValue(CourseState),
                doc="The state this course is in.",
            ),
            rqa.RequiredArgument(
                "tenant_id",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The id of the tenant that owns this course.",
            ),
            rqa.RequiredArgument(
                "copy_lock_date",
                rqa.SimpleValue.bool,
                doc=(
                    "Is the lock date feature enabled for this course. This"
                    " will be `True` for every course created after the"
                    " release of version N.2."
                ),
            ),
            rqa.RequiredArgument(
                "price",
                rqa.Nullable(parsers.ParserFor.make(CoursePrice)),
                doc="The price of this course.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "created_at": to_dict(self.created_at),
            "virtual": to_dict(self.virtual),
            "lti_provider": to_dict(self.lti_provider),
            "state": to_dict(self.state),
            "tenant_id": to_dict(self.tenant_id),
            "copy_lock_date": to_dict(self.copy_lock_date),
            "price": to_dict(self.price),
        }
        return res

    @classmethod
    def from_dict(cls: t.Type["Course"], d: t.Dict[str, t.Any]) -> "Course":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            created_at=parsed.created_at,
            virtual=parsed.virtual,
            lti_provider=parsed.lti_provider,
            state=parsed.state,
            tenant_id=parsed.tenant_id,
            copy_lock_date=parsed.copy_lock_date,
            price=parsed.price,
        )
        res.raw_data = d
        return res
