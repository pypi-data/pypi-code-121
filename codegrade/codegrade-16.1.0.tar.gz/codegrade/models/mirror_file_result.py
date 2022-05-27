"""The module that defines the ``MirrorFileResult`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class MirrorFileResult:
    """The result of a file that has been uploaded to mirror storage."""

    #: A complete url that can be used to download the file.
    url: "str"
    #: The filename under which the file can be downloaded. You can pass this
    #: to `/api/v1/files/<name>` to download the file.
    name: "str"
    #: The filename that the resulting file should have.
    output_name: "str"
    #: The mime type of the file, only available if known.
    mime: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "url",
                rqa.SimpleValue.str,
                doc="A complete url that can be used to download the file.",
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc=(
                    "The filename under which the file can be downloaded. You"
                    " can pass this to `/api/v1/files/<name>` to download the"
                    " file."
                ),
            ),
            rqa.RequiredArgument(
                "output_name",
                rqa.SimpleValue.str,
                doc="The filename that the resulting file should have.",
            ),
            rqa.RequiredArgument(
                "mime",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The mime type of the file, only available if known.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "url": to_dict(self.url),
            "name": to_dict(self.name),
            "output_name": to_dict(self.output_name),
            "mime": to_dict(self.mime),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["MirrorFileResult"], d: t.Dict[str, t.Any]
    ) -> "MirrorFileResult":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            url=parsed.url,
            name=parsed.name,
            output_name=parsed.output_name,
            mime=parsed.mime,
        )
        res.raw_data = d
        return res
