"""The module that defines the ``FeedbackBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .linter_comment import LinterComment


@dataclass
class FeedbackBase:
    """The base JSON representation for feedback."""

    #: The general feedback given on this submission.
    general: "str"
    #: A mapping that is almost the same the user feedback mapping for feedback
    #: without replies, only the final key is not a string but a list of tuples
    #: where the first item is the linter code and the second item is linter
    #: comments.
    linter: "t.Mapping[str, t.Mapping[str, t.Sequence[t.Sequence[t.Union[LinterComment, str]]]]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "general",
                rqa.SimpleValue.str,
                doc="The general feedback given on this submission.",
            ),
            rqa.RequiredArgument(
                "linter",
                rqa.LookupMapping(
                    rqa.LookupMapping(
                        rqa.List(
                            rqa.List(
                                parsers.make_union(
                                    parsers.ParserFor.make(LinterComment),
                                    rqa.SimpleValue.str,
                                )
                            )
                        )
                    )
                ),
                doc=(
                    "A mapping that is almost the same the user feedback"
                    " mapping for feedback without replies, only the final key"
                    " is not a string but a list of tuples where the first"
                    " item is the linter code and the second item is linter"
                    " comments."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "general": to_dict(self.general),
            "linter": to_dict(self.linter),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["FeedbackBase"], d: t.Dict[str, t.Any]
    ) -> "FeedbackBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            general=parsed.general,
            linter=parsed.linter,
        )
        res.raw_data = d
        return res
