"""The module that defines the ``UpdatePeerFeedbackSettingsAssignmentData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class UpdatePeerFeedbackSettingsAssignmentData:
    """Input data required for the `Assignment::UpdatePeerFeedbackSettings`
    operation.
    """

    #: The amount of subjects a single reviewer should give peer feedback on.
    amount: "int"
    #: The amount of time in seconds that a user has to give peer feedback
    #: after the deadline has expired.
    time: "t.Optional[datetime.timedelta]"
    #: Should peer feedback comments by default be approved.
    auto_approved: "bool"
    #: Should we redivide when a user submits its first submission or its last
    #: submission is deleted after thde deadline? If this is `False` it might
    #: happen that some users are reviewed by less or more than `amount` of
    #: students.
    redivide_after_deadline: "bool" = True

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "amount",
                rqa.SimpleValue.int,
                doc=(
                    "The amount of subjects a single reviewer should give peer"
                    " feedback on."
                ),
            ),
            rqa.RequiredArgument(
                "time",
                rqa.Nullable(rqa.RichValue.TimeDelta),
                doc=(
                    "The amount of time in seconds that a user has to give"
                    " peer feedback after the deadline has expired."
                ),
            ),
            rqa.RequiredArgument(
                "auto_approved",
                rqa.SimpleValue.bool,
                doc="Should peer feedback comments by default be approved.",
            ),
            rqa.DefaultArgument(
                "redivide_after_deadline",
                rqa.SimpleValue.bool,
                doc=(
                    "Should we redivide when a user submits its first"
                    " submission or its last submission is deleted after thde"
                    " deadline? If this is `False` it might happen that some"
                    " users are reviewed by less or more than `amount` of"
                    " students."
                ),
                default=lambda: True,
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "amount": to_dict(self.amount),
            "time": to_dict(self.time),
            "auto_approved": to_dict(self.auto_approved),
            "redivide_after_deadline": to_dict(self.redivide_after_deadline),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["UpdatePeerFeedbackSettingsAssignmentData"],
        d: t.Dict[str, t.Any],
    ) -> "UpdatePeerFeedbackSettingsAssignmentData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            amount=parsed.amount,
            time=parsed.time,
            auto_approved=parsed.auto_approved,
            redivide_after_deadline=parsed.redivide_after_deadline,
        )
        res.raw_data = d
        return res
