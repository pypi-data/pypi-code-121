"""The module that defines the ``About`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers
from ..utils import to_dict
from .base_about import BaseAbout
from .health_information import HealthInformation


@dataclass
class About(BaseAbout):
    """Information about this CodeGrade instance."""

    #: Health information, will only be present when the correct (secret)
    #: health key is provided.
    health: Maybe["HealthInformation"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseAbout.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.OptionalArgument(
                    "health",
                    parsers.ParserFor.make(HealthInformation),
                    doc=(
                        "Health information, will only be present when the"
                        " correct (secret) health key is provided."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.health = maybe_from_nullable(self.health)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "version": to_dict(self.version),
            "commit": to_dict(self.commit),
            "features": to_dict(self.features),
            "settings": to_dict(self.settings),
            "release": to_dict(self.release),
            "current_time": to_dict(self.current_time),
        }
        if self.health.is_just:
            res["health"] = to_dict(self.health.value)
        return res

    @classmethod
    def from_dict(cls: t.Type["About"], d: t.Dict[str, t.Any]) -> "About":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            version=parsed.version,
            commit=parsed.commit,
            features=parsed.features,
            settings=parsed.settings,
            release=parsed.release,
            current_time=parsed.current_time,
            health=parsed.health,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    import datetime

    from .frontend_site_settings import FrontendSiteSettings
    from .legacy_features import LegacyFeatures
    from .release_info import ReleaseInfo

    # fmt: on
