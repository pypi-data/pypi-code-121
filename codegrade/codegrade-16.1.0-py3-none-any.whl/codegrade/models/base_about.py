"""The module that defines the ``BaseAbout`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .frontend_site_settings import FrontendSiteSettings
from .legacy_features import LegacyFeatures
from .release_info import ReleaseInfo


@dataclass
class BaseAbout:
    """The base information about this instance."""

    #: What version is running on this server. Deprecated, please use `version`
    #: instead.
    version: "t.Optional[str]"
    #: The commit this server is running. Deprecated, please use `commit`
    #: instead.
    commit: "str"
    #: The features enabled on this instance. Deprecated, please use
    #: `settings`.
    features: "LegacyFeatures"
    #: The frontend settings and their values for this instance.
    settings: "FrontendSiteSettings"
    #: Information about the release running on this server.
    release: "ReleaseInfo"
    #: The current time on the server
    current_time: "datetime.datetime"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "version",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "What version is running on this server. Deprecated,"
                    " please use `version` instead."
                ),
            ),
            rqa.RequiredArgument(
                "commit",
                rqa.SimpleValue.str,
                doc=(
                    "The commit this server is running. Deprecated, please use"
                    " `commit` instead."
                ),
            ),
            rqa.RequiredArgument(
                "features",
                parsers.ParserFor.make(LegacyFeatures),
                doc=(
                    "The features enabled on this instance. Deprecated, please"
                    " use `settings`."
                ),
            ),
            rqa.RequiredArgument(
                "settings",
                parsers.ParserFor.make(FrontendSiteSettings),
                doc=(
                    "The frontend settings and their values for this instance."
                ),
            ),
            rqa.RequiredArgument(
                "release",
                parsers.ParserFor.make(ReleaseInfo),
                doc="Information about the release running on this server.",
            ),
            rqa.RequiredArgument(
                "current_time",
                rqa.RichValue.DateTime,
                doc="The current time on the server",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "version": to_dict(self.version),
            "commit": to_dict(self.commit),
            "features": to_dict(self.features),
            "settings": to_dict(self.settings),
            "release": to_dict(self.release),
            "current_time": to_dict(self.current_time),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseAbout"], d: t.Dict[str, t.Any]
    ) -> "BaseAbout":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            version=parsed.version,
            commit=parsed.commit,
            features=parsed.features,
            settings=parsed.settings,
            release=parsed.release,
            current_time=parsed.current_time,
        )
        res.raw_data = d
        return res
