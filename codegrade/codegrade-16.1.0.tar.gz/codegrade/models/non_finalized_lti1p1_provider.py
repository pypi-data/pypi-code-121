"""The module that defines the ``NonFinalizedLTI1p1Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_lti1p1_provider import BaseLTI1p1Provider


@dataclass
class NonFinalizedLTI1p1Provider(BaseLTI1p1Provider):
    """The JSON representation of a non finalized provider."""

    #: This is a non finalized provider, so it cannot yet be used for launches.
    finalized: "t.Literal[False]"
    #: The netloc the LTI provider should be configured on.
    netloc: "str"
    #: If you have the permission to edit this provider this will be a key with
    #: which you can do that.
    edit_secret: "t.Optional[str]"
    #: The consumer key used to connect the provider to an LMS.
    lms_consumer_key: "str"
    #: The shared secret used to connect the provider to an LMS.
    lms_consumer_secret: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseLTI1p1Provider.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "finalized",
                    rqa.LiteralBoolean(False),
                    doc=(
                        "This is a non finalized provider, so it cannot yet be"
                        " used for launches."
                    ),
                ),
                rqa.RequiredArgument(
                    "netloc",
                    rqa.SimpleValue.str,
                    doc="The netloc the LTI provider should be configured on.",
                ),
                rqa.RequiredArgument(
                    "edit_secret",
                    rqa.Nullable(rqa.SimpleValue.str),
                    doc=(
                        "If you have the permission to edit this provider this"
                        " will be a key with which you can do that."
                    ),
                ),
                rqa.RequiredArgument(
                    "lms_consumer_key",
                    rqa.SimpleValue.str,
                    doc=(
                        "The consumer key used to connect the provider to an"
                        " LMS."
                    ),
                ),
                rqa.RequiredArgument(
                    "lms_consumer_secret",
                    rqa.SimpleValue.str,
                    doc=(
                        "The shared secret used to connect the provider to an"
                        " LMS."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "finalized": to_dict(self.finalized),
            "netloc": to_dict(self.netloc),
            "edit_secret": to_dict(self.edit_secret),
            "lms_consumer_key": to_dict(self.lms_consumer_key),
            "lms_consumer_secret": to_dict(self.lms_consumer_secret),
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
        cls: t.Type["NonFinalizedLTI1p1Provider"], d: t.Dict[str, t.Any]
    ) -> "NonFinalizedLTI1p1Provider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            finalized=parsed.finalized,
            netloc=parsed.netloc,
            edit_secret=parsed.edit_secret,
            lms_consumer_key=parsed.lms_consumer_key,
            lms_consumer_secret=parsed.lms_consumer_secret,
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

    from .base_lti_provider import BaseLTIProvider

    # fmt: on
