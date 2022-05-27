"""The module that defines the ``BaseReleaseInfo`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class BaseReleaseInfo:
    """The part of the release info that will always be present."""

    #: The commit which is running on this server.
    commit: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "commit",
                rqa.SimpleValue.str,
                doc="The commit which is running on this server.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "commit": to_dict(self.commit),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseReleaseInfo"], d: t.Dict[str, t.Any]
    ) -> "BaseReleaseInfo":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            commit=parsed.commit,
        )
        res.raw_data = d
        return res
