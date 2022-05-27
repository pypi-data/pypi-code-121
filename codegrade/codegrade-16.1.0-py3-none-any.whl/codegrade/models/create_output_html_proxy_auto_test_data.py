"""The module that defines the ``CreateOutputHtmlProxyAutoTestData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CreateOutputHtmlProxyAutoTestData:
    """Input data required for the `AutoTest::CreateOutputHtmlProxy` operation."""

    #: Allow remote resources
    allow_remote_resources: "bool"
    #: Allow remote scripts
    allow_remote_scripts: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "allow_remote_resources",
                rqa.SimpleValue.bool,
                doc="Allow remote resources",
            ),
            rqa.RequiredArgument(
                "allow_remote_scripts",
                rqa.SimpleValue.bool,
                doc="Allow remote scripts",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "allow_remote_resources": to_dict(self.allow_remote_resources),
            "allow_remote_scripts": to_dict(self.allow_remote_scripts),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CreateOutputHtmlProxyAutoTestData"], d: t.Dict[str, t.Any]
    ) -> "CreateOutputHtmlProxyAutoTestData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            allow_remote_resources=parsed.allow_remote_resources,
            allow_remote_scripts=parsed.allow_remote_scripts,
        )
        res.raw_data = d
        return res
