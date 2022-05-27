"""The module that defines the ``LMSCapabilities`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class LMSCapabilities:
    """This class defines the capabilities of an LMS connected using LTI 1.3.

    An important note about naming in this class: most of the attribute names
    are not really intuitive. For example: *supporting* `set_deadline` means
    that we probably don't get the deadline from the LMS. This has two main
    reasons: 1) legacy: these strange names mirror the names used in our LTI
    1.1 classes, and 2) it describes what you can do inside CodeGrade with the
    LMS, maybe it is in the future possible to sync back the deadline to the
    LMS, and in this case the name `set_deadline` makes way more sense.
    """

    #: The name of the LMS.
    lms: "str"
    #: Is it possible for users to set the deadline of a CodeGrade assignment
    #: within CodeGrade?  This should be `True` if the LMS does **not** pass
    #: the deadline in the LTI launch, and `False` otherwise.
    set_deadline: "bool"
    #: Same as `set_deadline` but for the `lock_date` date.
    set_lock_date: "bool"
    #: Should the state of the assignment be set within CodeGrade and not be
    #: copied from the LMS?  If `False` users are not allowed to change to
    #: state of the assignment within CodeGrade (they can always set the state
    #: to done).
    set_state: "bool"
    #: Should the `available_at` of the assignment be set within CodeGrade and
    #: not be copied from the LMS?
    set_available_at: "bool"
    #: If there is a test student in the lms this its full name.
    test_student_name: "t.Optional[str]"
    #: The name of the iframe `postMessage` we can send to the LMS to notify
    #: that we want to set cookies in a full window.  This property is ugly,
    #: and shows that these capabilities are not really a very good
    #: abstraction: Only Canvas supports this, and it is not that likely that
    #: other LMSes will support this in the exact same way as Canvas does now.
    #: If set to `None` this LMS doesn't have any post message that will allow
    #: us to send cookies (this is currently the case for all LMSes except
    #: `Canvas`).
    cookie_post_message: "t.Optional[str]"
    #: A list of replacements groups (or namespaces) supported by this LMS.
    #: Some LMSes support more replacement variables than others, however we
    #: don't want to send replacement variables to an LMS we know it will never
    #: support. This property contains a list of custom replacement groups
    #: supported by this LMS.  For example: we have a replacement variable
    #: called `name'`, this variable will be included (parsed and returned as
    #: wanted config), if the `supported_custom_replacement_groups` contains
    #: `['$com']`. It will also be included if it contains `['$com',
    #: 'custom_lms']`. However, it will not be included if it only contains
    #: `custom_lms']` or `['$com', 'other_lms']`.
    supported_custom_replacement_groups: "t.Sequence[t.Sequence[str]]"
    #: Should we use the `id` in the url.  Some LMSes do not provide both the
    #: `iss` and the `client_id` in all launches. This means that finding the
    #: correct `LTI1p3Provider` is not always correct (especially as the `iss`
    #: often gets used multiple times). For some LMSes therefore it is a better
    #: idea to simply include the id of the provider in the launch url, and
    #: verify with the given information that the provider could theoretically
    #: be the correct one (i.e. all given information matches with the
    #: information in the LTI provider that belongs to the `id`).
    use_id_in_urls: "bool"
    #: Does this LMS require actual deep linking, where the user inputs a name
    #: and deadline.
    actual_deep_linking_required: "bool"
    #: Is it required to set a separate OAuth2 Audience for this LMS before we
    #: can finalize it.
    auth_audience_required: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "lms",
                rqa.SimpleValue.str,
                doc="The name of the LMS.",
            ),
            rqa.RequiredArgument(
                "set_deadline",
                rqa.SimpleValue.bool,
                doc=(
                    "Is it possible for users to set the deadline of a"
                    " CodeGrade assignment within CodeGrade?  This should be"
                    " `True` if the LMS does **not** pass the deadline in the"
                    " LTI launch, and `False` otherwise."
                ),
            ),
            rqa.RequiredArgument(
                "set_lock_date",
                rqa.SimpleValue.bool,
                doc="Same as `set_deadline` but for the `lock_date` date.",
            ),
            rqa.RequiredArgument(
                "set_state",
                rqa.SimpleValue.bool,
                doc=(
                    "Should the state of the assignment be set within"
                    " CodeGrade and not be copied from the LMS?  If `False`"
                    " users are not allowed to change to state of the"
                    " assignment within CodeGrade (they can always set the"
                    " state to done)."
                ),
            ),
            rqa.RequiredArgument(
                "set_available_at",
                rqa.SimpleValue.bool,
                doc=(
                    "Should the `available_at` of the assignment be set within"
                    " CodeGrade and not be copied from the LMS?"
                ),
            ),
            rqa.RequiredArgument(
                "test_student_name",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "If there is a test student in the lms this its full name."
                ),
            ),
            rqa.RequiredArgument(
                "cookie_post_message",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The name of the iframe `postMessage` we can send to the"
                    " LMS to notify that we want to set cookies in a full"
                    " window.  This property is ugly, and shows that these"
                    " capabilities are not really a very good abstraction:"
                    " Only Canvas supports this, and it is not that likely"
                    " that other LMSes will support this in the exact same way"
                    " as Canvas does now. If set to `None` this LMS doesn't"
                    " have any post message that will allow us to send cookies"
                    " (this is currently the case for all LMSes except"
                    " `Canvas`)."
                ),
            ),
            rqa.RequiredArgument(
                "supported_custom_replacement_groups",
                rqa.List(rqa.List(rqa.SimpleValue.str)),
                doc=(
                    "A list of replacements groups (or namespaces) supported"
                    " by this LMS.  Some LMSes support more replacement"
                    " variables than others, however we don't want to send"
                    " replacement variables to an LMS we know it will never"
                    " support. This property contains a list of custom"
                    " replacement groups supported by this LMS.  For example:"
                    " we have a replacement variable called `name'`, this"
                    " variable will be included (parsed and returned as wanted"
                    " config), if the `supported_custom_replacement_groups`"
                    " contains `['$com']`. It will also be included if it"
                    " contains `['$com', 'custom_lms']`. However, it will not"
                    " be included if it only contains `custom_lms']` or"
                    " `['$com', 'other_lms']`."
                ),
            ),
            rqa.RequiredArgument(
                "use_id_in_urls",
                rqa.SimpleValue.bool,
                doc=(
                    "Should we use the `id` in the url.  Some LMSes do not"
                    " provide both the `iss` and the `client_id` in all"
                    " launches. This means that finding the correct"
                    " `LTI1p3Provider` is not always correct (especially as"
                    " the `iss` often gets used multiple times). For some"
                    " LMSes therefore it is a better idea to simply include"
                    " the id of the provider in the launch url, and verify"
                    " with the given information that the provider could"
                    " theoretically be the correct one (i.e. all given"
                    " information matches with the information in the LTI"
                    " provider that belongs to the `id`)."
                ),
            ),
            rqa.RequiredArgument(
                "actual_deep_linking_required",
                rqa.SimpleValue.bool,
                doc=(
                    "Does this LMS require actual deep linking, where the user"
                    " inputs a name and deadline."
                ),
            ),
            rqa.RequiredArgument(
                "auth_audience_required",
                rqa.SimpleValue.bool,
                doc=(
                    "Is it required to set a separate OAuth2 Audience for this"
                    " LMS before we can finalize it."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "lms": to_dict(self.lms),
            "set_deadline": to_dict(self.set_deadline),
            "set_lock_date": to_dict(self.set_lock_date),
            "set_state": to_dict(self.set_state),
            "set_available_at": to_dict(self.set_available_at),
            "test_student_name": to_dict(self.test_student_name),
            "cookie_post_message": to_dict(self.cookie_post_message),
            "supported_custom_replacement_groups": to_dict(
                self.supported_custom_replacement_groups
            ),
            "use_id_in_urls": to_dict(self.use_id_in_urls),
            "actual_deep_linking_required": to_dict(
                self.actual_deep_linking_required
            ),
            "auth_audience_required": to_dict(self.auth_audience_required),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["LMSCapabilities"], d: t.Dict[str, t.Any]
    ) -> "LMSCapabilities":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            lms=parsed.lms,
            set_deadline=parsed.set_deadline,
            set_lock_date=parsed.set_lock_date,
            set_state=parsed.set_state,
            set_available_at=parsed.set_available_at,
            test_student_name=parsed.test_student_name,
            cookie_post_message=parsed.cookie_post_message,
            supported_custom_replacement_groups=parsed.supported_custom_replacement_groups,
            use_id_in_urls=parsed.use_id_in_urls,
            actual_deep_linking_required=parsed.actual_deep_linking_required,
            auth_audience_required=parsed.auth_audience_required,
        )
        res.raw_data = d
        return res
