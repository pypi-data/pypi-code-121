"""The module that defines the ``AutoTestStepLogBase`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class AutoTestStepLogBase:
    """The base AutoTestStep log for every step type.

    This is also the type of the log when the test hasn't been started yet.
    """

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping().use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AutoTestStepLogBase"], d: t.Dict[str, t.Any]
    ) -> "AutoTestStepLogBase":
        parsed = cls.data_parser.try_parse(d)

        res = cls()
        res.raw_data = d
        return res
