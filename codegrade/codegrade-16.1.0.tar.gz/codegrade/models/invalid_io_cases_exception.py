"""The module that defines the ``InvalidIOCasesException`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from .. import parsers
from ..utils import to_dict
from .auto_test_step_validation_exception import (
    AutoTestStepValidationException,
)


@dataclass
class InvalidIOCasesException(AutoTestStepValidationException):
    """The exception raised when an IO test contained invalid data."""

    #: The list of invalid cases. Each case is a two tuple of an int and a
    #: string. The int is the index of the case, and the string the error for
    #: that case. A single index might be present more than once.
    invalid_cases: "t.Sequence[t.Sequence[t.Union[int, str]]]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: AutoTestStepValidationException.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "invalid_cases",
                    rqa.List(
                        rqa.List(
                            parsers.make_union(
                                rqa.SimpleValue.int, rqa.SimpleValue.str
                            )
                        )
                    ),
                    doc=(
                        "The list of invalid cases. Each case is a two tuple"
                        " of an int and a string. The int is the index of the"
                        " case, and the string the error for that case. A"
                        " single index might be present more than once."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "invalid_cases": to_dict(self.invalid_cases),
            "step_idx": to_dict(self.step_idx),
            "message": to_dict(self.message),
            "description": to_dict(self.description),
            "code": to_dict(self.code),
            "request_id": to_dict(self.request_id),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["InvalidIOCasesException"],
        d: t.Dict[str, t.Any],
        response: t.Optional[Response] = None,
    ) -> "InvalidIOCasesException":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            invalid_cases=parsed.invalid_cases,
            step_idx=parsed.step_idx,
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
    from .base_error import BaseError

    # fmt: on
