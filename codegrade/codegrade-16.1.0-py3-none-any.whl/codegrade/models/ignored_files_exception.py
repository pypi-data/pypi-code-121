"""The module that defines the ``IgnoredFilesException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .base_error import BaseError
from .cg_ignore_version import CGIgnoreVersion
from .extract_file_tree_directory import ExtractFileTreeDirectory
from .file_deletion import FileDeletion
from .file_rule import FileRule
from .missing_file import MissingFile


@dataclass
class IgnoredFilesException(BaseError):
    """The exception used when invalid files were present in a submission."""

    #: The files that were removed.
    removed_files: "t.Sequence[FileDeletion]"
    #: The invalid files that were in the archive. This is a list of two
    #: tuples, where the first item is the full name of the invalid file, and
    #: the second item is the reason why the file/directory should be removed.
    invalid_files: "t.Sequence[t.Sequence[t.Union[FileRule, str]]]"
    #: The original tree that was submitted.
    original_tree: "ExtractFileTreeDirectory"
    #: The version of the filter that removed this version. Deprecated, use
    #: `filter_name` instead.
    filter_version: "int"
    #: The version of the filter that caused the error.
    filter_name: "CGIgnoreVersion"
    #: Which files are missing but are required.
    missing_files: "t.Sequence[MissingFile]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: BaseError.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "removed_files",
                    rqa.List(parsers.ParserFor.make(FileDeletion)),
                    doc="The files that were removed.",
                ),
                rqa.RequiredArgument(
                    "invalid_files",
                    rqa.List(
                        rqa.List(
                            parsers.make_union(
                                parsers.ParserFor.make(FileRule),
                                rqa.SimpleValue.str,
                            )
                        )
                    ),
                    doc=(
                        "The invalid files that were in the archive. This is a"
                        " list of two tuples, where the first item is the full"
                        " name of the invalid file, and the second item is the"
                        " reason why the file/directory should be removed."
                    ),
                ),
                rqa.RequiredArgument(
                    "original_tree",
                    parsers.ParserFor.make(ExtractFileTreeDirectory),
                    doc="The original tree that was submitted.",
                ),
                rqa.RequiredArgument(
                    "filter_version",
                    rqa.SimpleValue.int,
                    doc=(
                        "The version of the filter that removed this version."
                        " Deprecated, use `filter_name` instead."
                    ),
                ),
                rqa.RequiredArgument(
                    "filter_name",
                    rqa.EnumValue(CGIgnoreVersion),
                    doc="The version of the filter that caused the error.",
                ),
                rqa.RequiredArgument(
                    "missing_files",
                    rqa.List(parsers.ParserFor.make(MissingFile)),
                    doc="Which files are missing but are required.",
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "removed_files": to_dict(self.removed_files),
            "invalid_files": to_dict(self.invalid_files),
            "original_tree": to_dict(self.original_tree),
            "filter_version": to_dict(self.filter_version),
            "filter_name": to_dict(self.filter_name),
            "missing_files": to_dict(self.missing_files),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["IgnoredFilesException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "IgnoredFilesException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            removed_files=parsed.removed_files,
            invalid_files=parsed.invalid_files,
            original_tree=parsed.original_tree,
            filter_version=parsed.filter_version,
            filter_name=parsed.filter_name,
            missing_files=parsed.missing_files,
            message=parsed.message,
            description=parsed.description,
            code=parsed.code,
            request_id=parsed.request_id,
            response=response,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    from .api_codes import APICodes

    # fmt: on
