"""The module that defines the ``LTI1p3ProviderPresentationAsJSON`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LTI1p3ProviderPresentationAsJSON:
    """Settings relating to how CodeGrade should be presented to the user in
    this LTI provider.
    """

    #: The preferred height of the iframe CodeGrade is rendered in.
    preferred_frame_height: "t.Optional[int]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "preferred_frame_height",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The preferred height of the iframe CodeGrade is"
                    " rendered in."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "preferred_frame_height": to_dict(self.preferred_frame_height),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LTI1p3ProviderPresentationAsJSON"], d: t.Dict[str, t.Any]
    ) -> "LTI1p3ProviderPresentationAsJSON":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            preferred_frame_height=parsed.preferred_frame_height,
        )
        res.raw_data = d
        return res
