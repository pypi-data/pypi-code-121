"""The module that defines the ``AssignmentPeerFeedbackConnection`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .user import User


@dataclass
class AssignmentPeerFeedbackConnection:
    """A peer feedback connection that connects two students."""

    #: The user that should be given a review.
    subject: "User"
    #: The user that should do the review.
    peer: "User"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "subject",
                parsers.ParserFor.make(User),
                doc="The user that should be given a review.",
            ),
            rqa.RequiredArgument(
                "peer",
                parsers.ParserFor.make(User),
                doc="The user that should do the review.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "subject": to_dict(self.subject),
            "peer": to_dict(self.peer),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AssignmentPeerFeedbackConnection"], d: t.Dict[str, t.Any]
    ) -> "AssignmentPeerFeedbackConnection":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            subject=parsed.subject,
            peer=parsed.peer,
        )
        res.raw_data = d
        return res
