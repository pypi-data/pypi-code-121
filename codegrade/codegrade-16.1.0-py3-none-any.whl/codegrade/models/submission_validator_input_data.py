"""The module that defines the ``SubmissionValidatorInputData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .file_rule_input_data import FileRuleInputData
from .options_input_data import OptionsInputData


@dataclass
class SubmissionValidatorInputData:
    """The input data for the SubmissionValidator ignore type."""

    #: The default policy of this validator.
    policy: "t.Literal['allow_all_files', 'deny_all_files']"
    #: The rules in this validator. If the policy is "deny\_all\_files" this
    #: should not be empty.
    rules: "t.Sequence[FileRuleInputData]"
    #: The options for this validator.
    options: "t.Sequence[OptionsInputData]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "policy",
                rqa.StringEnum("allow_all_files", "deny_all_files"),
                doc="The default policy of this validator.",
            ),
            rqa.RequiredArgument(
                "rules",
                rqa.List(parsers.ParserFor.make(FileRuleInputData)),
                doc=(
                    "The rules in this validator. If the policy is"
                    ' "deny\\_all\\_files" this should not be empty.'
                ),
            ),
            rqa.RequiredArgument(
                "options",
                rqa.List(parsers.ParserFor.make(OptionsInputData)),
                doc="The options for this validator.",
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "policy": to_dict(self.policy),
            "rules": to_dict(self.rules),
            "options": to_dict(self.options),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["SubmissionValidatorInputData"], d: t.Dict[str, t.Any]
    ) -> "SubmissionValidatorInputData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            policy=parsed.policy,
            rules=parsed.rules,
            options=parsed.options,
        )
        res.raw_data = d
        return res
