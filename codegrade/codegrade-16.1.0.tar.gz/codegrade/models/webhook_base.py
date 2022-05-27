"""The module that defines the ``WebhookBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class WebhookBase:
    """The configuration for a webhook."""

    #: The id of the webhook configuration.
    id: "str"
    #: The public key that we will use to clone the repository.
    public_key: "str"
    #: The id of the assignment to which this config is connected.
    assignment_id: "int"
    #: The user that owns this configuration. Submissions made by this config
    #: will have this user as author.
    user_id: "int"
    #: The secret that should be passed in the webhook by the provider (e.g.
    #: GitHub).
    secret: "str"
    #: The default branch configured by the teacher, currently not used.
    default_branch: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the webhook configuration.",
            ),
            rqa.RequiredArgument(
                "public_key",
                rqa.SimpleValue.str,
                doc="The public key that we will use to clone the repository.",
            ),
            rqa.RequiredArgument(
                "assignment_id",
                rqa.SimpleValue.int,
                doc=(
                    "The id of the assignment to which this config is"
                    " connected."
                ),
            ),
            rqa.RequiredArgument(
                "user_id",
                rqa.SimpleValue.int,
                doc=(
                    "The user that owns this configuration. Submissions made"
                    " by this config will have this user as author."
                ),
            ),
            rqa.RequiredArgument(
                "secret",
                rqa.SimpleValue.str,
                doc=(
                    "The secret that should be passed in the webhook by the"
                    " provider (e.g. GitHub)."
                ),
            ),
            rqa.RequiredArgument(
                "default_branch",
                rqa.SimpleValue.str,
                doc=(
                    "The default branch configured by the teacher, currently"
                    " not used."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "public_key": to_dict(self.public_key),
            "assignment_id": to_dict(self.assignment_id),
            "user_id": to_dict(self.user_id),
            "secret": to_dict(self.secret),
            "default_branch": to_dict(self.default_branch),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["WebhookBase"], d: t.Dict[str, t.Any]
    ) -> "WebhookBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            public_key=parsed.public_key,
            assignment_id=parsed.assignment_id,
            user_id=parsed.user_id,
            secret=parsed.secret,
            default_branch=parsed.default_branch,
        )
        res.raw_data = d
        return res
