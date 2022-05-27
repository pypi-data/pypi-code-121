"""The module that defines the ``FinalizedLTI1p1Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_lti1p1_provider import BaseLTI1p1Provider


@dataclass
class FinalizedLTI1p1Provider(BaseLTI1p1Provider):
    """The JSON representation of a finalized provider."""

    #: This is a already finalized provider and thus is actively being used.
    finalized: "t.Literal[True]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseLTI1p1Provider.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "finalized",
                    rqa.LiteralBoolean(True),
                    doc=(
                        "This is a already finalized provider and thus is"
                        " actively being used."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "finalized": to_dict(self.finalized),
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
        cls: t.Type["FinalizedLTI1p1Provider"], d: t.Dict[str, t.Any]
    ) -> "FinalizedLTI1p1Provider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            finalized=parsed.finalized,
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
