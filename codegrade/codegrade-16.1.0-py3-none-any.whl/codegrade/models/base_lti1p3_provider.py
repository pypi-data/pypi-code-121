"""The module that defines the ``BaseLTI1p3Provider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .base_lti_provider import BaseLTIProvider
from .lms_capabilities import LMSCapabilities
from .lti1p3_provider_presentation_as_json import (
    LTI1p3ProviderPresentationAsJSON,
)


@dataclass
class BaseLTI1p3Provider(BaseLTIProvider):
    """The base representation of an LTI 1.3 provider."""

    #: The LMS that is connected as this LTI provider.
    lms: "t.Literal['Blackboard', 'Brightspace', 'Canvas', 'Moodle']"
    #: The capabilities of this LMS
    capabilities: "LMSCapabilities"
    #: The LTI version used.
    version: "t.Literal['lti1.3']"
    #: The iss configured for this provider.
    iss: "str"
    #: Presentational settings for this provider.
    presentation: "LTI1p3ProviderPresentationAsJSON"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseLTIProvider.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "lms",
                    rqa.StringEnum(
                        "Blackboard", "Brightspace", "Canvas", "Moodle"
                    ),
                    doc="The LMS that is connected as this LTI provider.",
                ),
                rqa.RequiredArgument(
                    "capabilities",
                    parsers.ParserFor.make(LMSCapabilities),
                    doc="The capabilities of this LMS",
                ),
                rqa.RequiredArgument(
                    "version",
                    rqa.StringEnum("lti1.3"),
                    doc="The LTI version used.",
                ),
                rqa.RequiredArgument(
                    "iss",
                    rqa.SimpleValue.str,
                    doc="The iss configured for this provider.",
                ),
                rqa.RequiredArgument(
                    "presentation",
                    parsers.ParserFor.make(LTI1p3ProviderPresentationAsJSON),
                    doc="Presentational settings for this provider.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
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
        cls: t.Type["BaseLTI1p3Provider"], d: t.Dict[str, t.Any]
    ) -> "BaseLTI1p3Provider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
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

    # fmt: on
