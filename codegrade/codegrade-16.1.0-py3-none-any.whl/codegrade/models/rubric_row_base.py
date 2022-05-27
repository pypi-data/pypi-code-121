"""The module that defines the ``RubricRowBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .rubric_description_type import RubricDescriptionType
from .rubric_item import RubricItem
from .rubric_lock_reason import RubricLockReason


@dataclass
class RubricRowBase:
    """The JSON representation of a rubric row."""

    #: The id of this row, used for updating
    id: "int"
    #: The header of this row.
    header: "str"
    #: The description of this row.
    description: "t.Optional[str]"
    #: The type of descriptions in this row.
    description_type: "RubricDescriptionType"
    #: The item in this row. The length will always be 1 for continuous rubric
    #: rows.
    items: "t.Sequence[RubricItem]"
    #: Is this row locked. If it is locked you cannot update it, nor can you
    #: manually select items in it.
    locked: "t.Union[RubricLockReason, t.Literal[False]]"
    #: The type of rubric row.
    type: "str"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of this row, used for updating",
            ),
            rqa.RequiredArgument(
                "header",
                rqa.SimpleValue.str,
                doc="The header of this row.",
            ),
            rqa.RequiredArgument(
                "description",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The description of this row.",
            ),
            rqa.RequiredArgument(
                "description_type",
                rqa.EnumValue(RubricDescriptionType),
                doc="The type of descriptions in this row.",
            ),
            rqa.RequiredArgument(
                "items",
                rqa.List(parsers.ParserFor.make(RubricItem)),
                doc=(
                    "The item in this row. The length will always be 1 for"
                    " continuous rubric rows."
                ),
            ),
            rqa.RequiredArgument(
                "locked",
                parsers.make_union(
                    rqa.EnumValue(RubricLockReason), rqa.LiteralBoolean(False)
                ),
                doc=(
                    "Is this row locked. If it is locked you cannot update it,"
                    " nor can you manually select items in it."
                ),
            ),
            rqa.RequiredArgument(
                "type",
                rqa.SimpleValue.str,
                doc="The type of rubric row.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "header": to_dict(self.header),
            "description": to_dict(self.description),
            "description_type": to_dict(self.description_type),
            "items": to_dict(self.items),
            "locked": to_dict(self.locked),
            "type": to_dict(self.type),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["RubricRowBase"], d: t.Dict[str, t.Any]
    ) -> "RubricRowBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            header=parsed.header,
            description=parsed.description,
            description_type=parsed.description_type,
            items=parsed.items,
            locked=parsed.locked,
            type=parsed.type,
        )
        res.raw_data = d
        return res
