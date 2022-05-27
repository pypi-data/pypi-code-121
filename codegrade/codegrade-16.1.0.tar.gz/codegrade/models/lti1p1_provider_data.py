"""The module that defines the ``LTI1p1ProviderData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LTI1p1ProviderData:
    """ """

    #: The id of the tenant that will use this LMS
    tenant_id: "str"
    #: The LMS that will be used for this connection
    lms: "t.Literal['Canvas', 'Blackboard', 'Sakai', 'Thought Industries', 'Open edX', 'Moodle', 'BrightSpace', 'Populi']"
    #: Use LTI 1.1
    lti_version: "t.Literal['lti1.1']"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "tenant_id",
                rqa.SimpleValue.str,
                doc="The id of the tenant that will use this LMS",
            ),
            rqa.RequiredArgument(
                "lms",
                rqa.StringEnum(
                    "Canvas",
                    "Blackboard",
                    "Sakai",
                    "Thought Industries",
                    "Open edX",
                    "Moodle",
                    "BrightSpace",
                    "Populi",
                ),
                doc="The LMS that will be used for this connection",
            ),
            rqa.RequiredArgument(
                "lti_version",
                rqa.StringEnum("lti1.1"),
                doc="Use LTI 1.1",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "tenant_id": to_dict(self.tenant_id),
            "lms": to_dict(self.lms),
            "lti_version": to_dict(self.lti_version),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LTI1p1ProviderData"], d: t.Dict[str, t.Any]
    ) -> "LTI1p1ProviderData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            tenant_id=parsed.tenant_id,
            lms=parsed.lms,
            lti_version=parsed.lti_version,
        )
        res.raw_data = d
        return res
