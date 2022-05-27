"""The module that defines the ``Patch1P1ProviderLTIData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class Patch1P1ProviderLTIData:
    """Input data required for the `LTI::Patch1P1Provider` operation."""

    #: Should this provider be finalized.
    finalize: Maybe["bool"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "finalize",
                rqa.SimpleValue.bool,
                doc="Should this provider be finalized.",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.finalize = maybe_from_nullable(self.finalize)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.finalize.is_just:
            res["finalize"] = to_dict(self.finalize.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["Patch1P1ProviderLTIData"], d: t.Dict[str, t.Any]
    ) -> "Patch1P1ProviderLTIData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            finalize=parsed.finalize,
        )
        res.raw_data = d
        return res
