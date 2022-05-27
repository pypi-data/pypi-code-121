"""The module that defines the ``OAuthProvider`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class OAuthProvider:
    """A connection to a provider that implements the "authorization server"
    part of RFC6749.
    """

    #: The id of the provider.
    id: "str"
    #: The name of the OAuth provider.
    name: "str"
    #: The platform of this provider.
    platform: "t.Literal['github', 'gitlab']"
    #: The base URL of the provider.
    base_url: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of the provider.",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the OAuth provider.",
            ),
            rqa.RequiredArgument(
                "platform",
                rqa.StringEnum("github", "gitlab"),
                doc="The platform of this provider.",
            ),
            rqa.RequiredArgument(
                "base_url",
                rqa.SimpleValue.str,
                doc="The base URL of the provider.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "platform": to_dict(self.platform),
            "base_url": to_dict(self.base_url),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["OAuthProvider"], d: t.Dict[str, t.Any]
    ) -> "OAuthProvider":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            platform=parsed.platform,
            base_url=parsed.base_url,
        )
        res.raw_data = d
        return res
