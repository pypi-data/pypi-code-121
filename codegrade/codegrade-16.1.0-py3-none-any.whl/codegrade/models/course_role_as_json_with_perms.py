"""The module that defines the ``CourseRoleAsJSONWithPerms`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .course_perm_map import CoursePermMap
from .course_role import CourseRole


@dataclass
class CourseRoleAsJSONWithPerms(CourseRole):
    """The JSON representation of a role including the permissions the role
    has.
    """

    #: The permissions this role has
    perms: "CoursePermMap"
    #: Is the currently logged in user enrolled in the course as this role.
    own: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: CourseRole.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "perms",
                    parsers.ParserFor.make(CoursePermMap),
                    doc="The permissions this role has",
                ),
                rqa.RequiredArgument(
                    "own",
                    rqa.SimpleValue.bool,
                    doc=(
                        "Is the currently logged in user enrolled in the"
                        " course as this role."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "perms": to_dict(self.perms),
            "own": to_dict(self.own),
            "course": to_dict(self.course),
            "hidden": to_dict(self.hidden),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseRoleAsJSONWithPerms"], d: t.Dict[str, t.Any]
    ) -> "CourseRoleAsJSONWithPerms":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            perms=parsed.perms,
            own=parsed.own,
            course=parsed.course,
            hidden=parsed.hidden,
            id=parsed.id,
            name=parsed.name,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .abstract_role import AbstractRole
    from .course import Course

    # fmt: on
