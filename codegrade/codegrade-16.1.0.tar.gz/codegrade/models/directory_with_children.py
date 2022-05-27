"""The module that defines the ``DirectoryWithChildren`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .base_directory import BaseDirectory
from .base_file import BaseFile


@dataclass
class DirectoryWithChildren(BaseDirectory):
    """A directory represented as JSON."""

    #: The entries in this directory. This is a list that will contain all
    #: children of the directory. This key might not be present, in which case
    #: the file is not a directory.
    entries: "t.Sequence[t.Union[BaseFile, DirectoryWithChildren]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseDirectory.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "entries",
                    rqa.List(
                        parsers.make_union(
                            parsers.ParserFor.make(BaseFile),
                            parsers.ParserFor.make(DirectoryWithChildren),
                        )
                    ),
                    doc=(
                        "The entries in this directory. This is a list that"
                        " will contain all children of the directory. This key"
                        " might not be present, in which case the file is not"
                        " a directory."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "entries": to_dict(self.entries),
            "type": to_dict(self.type),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["DirectoryWithChildren"], d: t.Dict[str, t.Any]
    ) -> "DirectoryWithChildren":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            entries=parsed.entries,
            type=parsed.type,
            id=parsed.id,
            name=parsed.name,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
