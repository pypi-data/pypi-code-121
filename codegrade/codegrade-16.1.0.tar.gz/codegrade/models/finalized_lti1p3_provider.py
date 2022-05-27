"""The module that defines the ``FinalizedLTI1p3Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .base_lti1p3_provider import BaseLTI1p3Provider


@dataclass
class FinalizedLTI1p3Provider(BaseLTI1p3Provider):
    """A finalized LTI 1.3 provider as JSON."""

    #: This is a finalized provider.
    finalized: "t.Literal[True]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseLTI1p3Provider.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "finalized",
                    rqa.LiteralBoolean(True),
                    doc="This is a finalized provider.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "finalized": to_dict(self.finalized),
            "lms": to_dict(self.lms),
            "capabilities": to_dict(self.capabilities),
            "version": to_dict(self.version),
            "iss": to_dict(self.iss),
            "presentation": to_dict(self.presentation),
            "id": to_dict(self.id),
            "created_at": to_dict(self.created_at),
            "intended_use": to_dict(self.intended_use),
            "tenant_id": to_dict(self.tenant_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FinalizedLTI1p3Provider"], d: t.Dict[str, t.Any]
    ) -> "FinalizedLTI1p3Provider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            finalized=parsed.finalized,
            lms=parsed.lms,
            capabilities=parsed.capabilities,
            version=parsed.version,
            iss=parsed.iss,
            presentation=parsed.presentation,
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
    from .lms_capabilities import LMSCapabilities
    from .lti1p3_provider_presentation_as_json import (
        LTI1p3ProviderPresentationAsJSON,
    )

    # fmt: on
