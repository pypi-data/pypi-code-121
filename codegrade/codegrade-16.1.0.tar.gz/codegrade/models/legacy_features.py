"""The module that defines the ``LegacyFeatures`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LegacyFeatures:
    """The legacy features of CodeGrade.

    Please don't use this object, but instead check for enabled settings.
    """

    #: See settings.
    automatic_lti_role: "bool"
    #: See settings.
    auto_test: "bool"
    #: See settings.
    blackboard_zip_upload: "bool"
    #: See settings.
    course_register: "bool"
    #: See settings.
    email_students: "bool"
    #: See settings.
    groups: "bool"
    #: See settings.
    incremental_rubric_submission: "bool"
    #: See settings.
    lti: "bool"
    #: See settings.
    peer_feedback: "bool"
    #: See settings.
    register: "bool"
    #: See settings.
    render_html: "bool"
    #: See settings.
    rubrics: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "AUTOMATIC_LTI_ROLE",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "AUTO_TEST",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "BLACKBOARD_ZIP_UPLOAD",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "COURSE_REGISTER",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "EMAIL_STUDENTS",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "GROUPS",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "INCREMENTAL_RUBRIC_SUBMISSION",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "LTI",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "PEER_FEEDBACK",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "REGISTER",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "RENDER_HTML",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
            rqa.RequiredArgument(
                "RUBRICS",
                rqa.SimpleValue.bool,
                doc="See settings.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "AUTOMATIC_LTI_ROLE": to_dict(self.automatic_lti_role),
            "AUTO_TEST": to_dict(self.auto_test),
            "BLACKBOARD_ZIP_UPLOAD": to_dict(self.blackboard_zip_upload),
            "COURSE_REGISTER": to_dict(self.course_register),
            "EMAIL_STUDENTS": to_dict(self.email_students),
            "GROUPS": to_dict(self.groups),
            "INCREMENTAL_RUBRIC_SUBMISSION": to_dict(
                self.incremental_rubric_submission
            ),
            "LTI": to_dict(self.lti),
            "PEER_FEEDBACK": to_dict(self.peer_feedback),
            "REGISTER": to_dict(self.register),
            "RENDER_HTML": to_dict(self.render_html),
            "RUBRICS": to_dict(self.rubrics),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LegacyFeatures"], d: t.Dict[str, t.Any]
    ) -> "LegacyFeatures":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            automatic_lti_role=parsed.AUTOMATIC_LTI_ROLE,
            auto_test=parsed.AUTO_TEST,
            blackboard_zip_upload=parsed.BLACKBOARD_ZIP_UPLOAD,
            course_register=parsed.COURSE_REGISTER,
            email_students=parsed.EMAIL_STUDENTS,
            groups=parsed.GROUPS,
            incremental_rubric_submission=parsed.INCREMENTAL_RUBRIC_SUBMISSION,
            lti=parsed.LTI,
            peer_feedback=parsed.PEER_FEEDBACK,
            register=parsed.REGISTER,
            render_html=parsed.RENDER_HTML,
            rubrics=parsed.RUBRICS,
        )
        res.raw_data = d
        return res
