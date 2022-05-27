"""The module that defines the ``GitRepositoryLike`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class GitRepositoryLike:
    """A class representing an abstract Git repository."""

    #: The id of a repository
    id: "str"
    #: The name of the repository.
    name: "str"
    #: The URL of the repository.
    url: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of a repository",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the repository.",
            ),
            rqa.RequiredArgument(
                "url",
                rqa.SimpleValue.str,
                doc="The URL of the repository.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "url": to_dict(self.url),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GitRepositoryLike"], d: t.Dict[str, t.Any]
    ) -> "GitRepositoryLike":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            name=parsed.name,
            url=parsed.url,
        )
        res.raw_data = d
        return res
