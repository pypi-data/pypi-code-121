"""The module that defines the ``GitRepositoriesPage`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .git_repository_like import GitRepositoryLike


@dataclass
class GitRepositoriesPage:
    """The result of a single page of git repositories."""

    #: The repositories of this page. This can be empty even for non last
    #: pages.
    data: "t.Sequence[GitRepositoryLike]"
    #: If there is a next page the cursor to get them.
    cursor: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "data",
                rqa.List(parsers.ParserFor.make(GitRepositoryLike)),
                doc=(
                    "The repositories of this page. This can be empty even for"
                    " non last pages."
                ),
            ),
            rqa.RequiredArgument(
                "cursor",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="If there is a next page the cursor to get them.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "data": to_dict(self.data),
            "cursor": to_dict(self.cursor),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["GitRepositoriesPage"], d: t.Dict[str, t.Any]
    ) -> "GitRepositoriesPage":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            data=parsed.data,
            cursor=parsed.cursor,
        )
        res.raw_data = d
        return res
