"""The module that defines the ``BaseLTI1p1Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_lti_provider import BaseLTIProvider


@dataclass
class BaseLTI1p1Provider(BaseLTIProvider):
    """The base JSON representation of a LTI 1.1 provider."""

    #: The LMS that is connected as this LTI provider.
    lms: "t.Literal['Blackboard', 'BrightSpace', 'Canvas', 'Moodle', 'Open edX', 'Populi', 'Sakai', 'Thought Industries']"
    #: The LTI version used.
    version: "t.Literal['lti1.1']"
    #: Can you set the `lock_date` of assignment connected to this LTI
    #: provider?
    supports_lock_date: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseLTIProvider.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "lms",
                    rqa.StringEnum(
                        "Blackboard",
                        "BrightSpace",
                        "Canvas",
                        "Moodle",
                        "Open edX",
                        "Populi",
                        "Sakai",
                        "Thought Industries",
                    ),
                    doc="The LMS that is connected as this LTI provider.",
                ),
                rqa.RequiredArgument(
                    "version",
                    rqa.StringEnum("lti1.1"),
                    doc="The LTI version used.",
                ),
                rqa.RequiredArgument(
                    "supports_lock_date",
                    rqa.SimpleValue.bool,
                    doc=(
                        "Can you set the `lock_date` of assignment connected"
                        " to this LTI provider?"
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "lms": to_dict(self.lms),
            "version": to_dict(self.version),
            "supports_lock_date": to_dict(self.supports_lock_date),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "intended_use": to_dict(self.intended_use),
            "tenant_id": to_dict(self.tenant_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseLTI1p1Provider"], d: t.Dict[str, t.Any]
    ) -> "BaseLTI1p1Provider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            lms=parsed.lms,
            version=parsed.version,
            supports_lock_date=parsed.supports_lock_date,
            id=parsed.id,
            created_at=parsed.created_at,
            intended_use=parsed.intended_use,
            tenant_id=parsed.tenant_id,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    # fmt: on
