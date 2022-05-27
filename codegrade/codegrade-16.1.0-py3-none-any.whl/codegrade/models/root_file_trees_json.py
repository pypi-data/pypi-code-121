"""The module that defines the ``RootFileTreesJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .file_tree import FileTree, FileTreeParser


@dataclass
class RootFileTreesJSON:
    """A representation containing both the teacher file tree and student file
    tree for a submission.
    """

    #: The teacher file tree, this will be `null` if you do not have the
    #: permission to see teacher files. This might be exactly the same as the
    #: student tree.
    teacher: "t.Optional[FileTree]"
    student: "FileTree"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "teacher",
                rqa.Nullable(FileTreeParser),
                doc=(
                    "The teacher file tree, this will be `null` if you do not"
                    " have the permission to see teacher files. This might be"
                    " exactly the same as the student tree."
                ),
            ),
            rqa.RequiredArgument(
                "student",
                FileTreeParser,
                doc="",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "teacher": to_dict(self.teacher),
            "student": to_dict(self.student),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RootFileTreesJSON"], d: t.Dict[str, t.Any]
    ) -> "RootFileTreesJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            teacher=parsed.teacher,
            student=parsed.student,
        )
        res.raw_data = d
        return res
