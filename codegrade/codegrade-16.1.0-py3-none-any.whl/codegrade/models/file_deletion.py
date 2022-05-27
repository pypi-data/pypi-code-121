"""The module that defines the ``FileDeletion`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .deletion_type import DeletionType
from .file_rule import FileRule


@dataclass
class FileDeletion:
    """A file that was deleted because of a ignore rule."""

    #: The full name of the deleted file or directory.
    fullname: "str"
    #: The reason it was removed.
    reason: "t.Union[FileRule, str]"
    #: The type of deletion.
    deletion_type: "DeletionType"
    #: The name of the file, not including any preceding directories.
    name: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "fullname",
                rqa.SimpleValue.str,
                doc="The full name of the deleted file or directory.",
            ),
            rqa.RequiredArgument(
                "reason",
                parsers.make_union(
                    parsers.ParserFor.make(FileRule), rqa.SimpleValue.str
                ),
                doc="The reason it was removed.",
            ),
            rqa.RequiredArgument(
                "deletion_type",
                rqa.EnumValue(DeletionType),
                doc="The type of deletion.",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc=(
                    "The name of the file, not including any preceding"
                    " directories."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "fullname": to_dict(self.fullname),
            "reason": to_dict(self.reason),
            "deletion_type": to_dict(self.deletion_type),
            "name": to_dict(self.name),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FileDeletion"], d: t.Dict[str, t.Any]
    ) -> "FileDeletion":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            fullname=parsed.fullname,
            reason=parsed.reason,
            deletion_type=parsed.deletion_type,
            name=parsed.name,
        )
        res.raw_data = d
        return res
