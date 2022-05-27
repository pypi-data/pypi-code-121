"""The module that defines the ``ExtractFileTreeDirectory`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .extract_file_tree_file import ExtractFileTreeFile


@dataclass
class ExtractFileTreeDirectory(ExtractFileTreeFile):
    """The JSON representation of a dir."""

    #: The entries in the directory.
    entries: "t.Sequence[t.Union[ExtractFileTreeDirectory, ExtractFileTreeFile]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: ExtractFileTreeFile.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "entries",
                    rqa.List(
                        parsers.make_union(
                            parsers.ParserFor.make(ExtractFileTreeDirectory),
                            parsers.ParserFor.make(ExtractFileTreeFile),
                        )
                    ),
                    doc="The entries in the directory.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "entries": to_dict(self.entries),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["ExtractFileTreeDirectory"], d: t.Dict[str, t.Any]
    ) -> "ExtractFileTreeDirectory":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            entries=parsed.entries,
            name=parsed.name,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
