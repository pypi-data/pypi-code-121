"""The module that defines the ``CourseRegisterResponse`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CourseRegisterResponse:
    """Response when a new user registered with a course registration link."""

    #: The access token that the created user can use to log in.
    access_token: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "access_token",
                rqa.SimpleValue.str,
                doc=(
                    "The access token that the created user can use to log in."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "access_token": to_dict(self.access_token),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CourseRegisterResponse"], d: t.Dict[str, t.Any]
    ) -> "CourseRegisterResponse":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            access_token=parsed.access_token,
        )
        res.raw_data = d
        return res
