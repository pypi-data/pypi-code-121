"""The module that defines the ``BaseFile`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class BaseFile:
    """The base JSON representation of a file."""

    #: This is a file, not a directory.
    type: "t.Literal['file']"
    #: The id of this file
    id: "str"
    #: The local name of this file, this does **not** include any parent
    #: directory names, nor does it include trailing slashes for directories.
    name: "str"
    #: If we already know the file size of this file this will be provided
    #: here.
    size: "t.Optional[int]"
    #: The hash of the file contents if we know this.
    hash: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "type",
                rqa.StringEnum("file"),
                doc="This is a file, not a directory.",
            ),
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.str,
                doc="The id of this file",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc=(
                    "The local name of this file, this does **not** include"
                    " any parent directory names, nor does it include trailing"
                    " slashes for directories."
                ),
            ),
            rqa.RequiredArgument(
                "size",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "If we already know the file size of this file this will"
                    " be provided here."
                ),
            ),
            rqa.RequiredArgument(
                "hash",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The hash of the file contents if we know this.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "type": to_dict(self.type),
            "id": to_dict(self.id),
            "name": to_dict(self.name),
            "size": to_dict(self.size),
            "hash": to_dict(self.hash),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["BaseFile"], d: t.Dict[str, t.Any]
    ) -> "BaseFile":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            type=parsed.type,
            id=parsed.id,
            name=parsed.name,
            size=parsed.size,
            hash=parsed.hash,
        )
        res.raw_data = d
        return res
