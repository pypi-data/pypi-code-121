"""The module that defines the ``Assignment`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from .. import parsers
from ..utils import to_dict
from .assignment_anonymization_algo import AssignmentAnonymizationAlgo
from .assignment_grading_settings_as_json import (
    AssignmentGradingSettingsAsJSON,
)
from .assignment_kind import AssignmentKind
from .assignment_peer_feedback_settings import AssignmentPeerFeedbackSettings
from .cg_ignore_version import CGIgnoreVersion
from .group_set import GroupSet
from .submission_validator_input_data import SubmissionValidatorInputData


@dataclass
class Assignment:
    """The serialization of an assignment.

    See the comments in the source code for the meaning of each field.
    """

    #: The id of the assignment.
    id: "int"
    #: Current state of the assignment.
    state: "t.Literal['done', 'grading', 'hidden', 'submitting']"
    #: Description of the assignment.
    description: "t.Optional[str]"
    #: When this assignment was created.
    created_at: "datetime.datetime"
    #: The deadline of the assignment. It is possible the assignment has no
    #: deadline yet, in which case it will be `None`.
    deadline: "t.Optional[datetime.datetime]"
    #: The moment this assignment locks, this can be seen as a form of second
    #: deadline.
    lock_date: "t.Optional[datetime.datetime]"
    #: The name of the assignment.
    name: "str"
    #: Is this an LTI assignment.
    is_lti: "bool"
    #: Course of this assignment.
    course_id: "int"
    #: The cginore.
    cgignore: "t.Optional[t.Union[SubmissionValidatorInputData, str]]"
    #: The version of the cignore file.
    cgignore_version: "t.Optional[CGIgnoreVersion]"
    #: The time the assignment will become available (i.e. the state will
    #: switch from 'hidden' to 'open'). If the state is not 'hidden' this value
    #: has no meaning. If this value is not `None` you cannot change to state
    #: to 'hidden' or 'open'.
    available_at: "t.Optional[datetime.datetime]"
    #: Should we send login links to all users before the `available_at` time.
    send_login_links: "bool"
    #: The fixed value for the maximum that can be achieved in a rubric. This
    #: can be higher and lower than the actual max. Will be `None` if unset.
    fixed_max_rubric_points: "t.Optional[float]"
    #: The maximum grade you can get for this assignment. This is based around
    #: the idea that a 10 is a 'perfect' score. So if this value is 12 a user
    #: can score 2 additional bonus points. If this value is `None` it is unset
    #: and regarded as a 10.
    max_grade: "t.Optional[float]"
    #: Settings that influence how the grade for a submission can be
    #: determined. TODO: Should we also move max\_grade and/or
    #: fixed\_max\_rubric\_points to the grading object?
    grading: "AssignmentGradingSettingsAsJSON"
    #: The group set of this assignment. This is `None` if this assignment is
    #: not a group assignment.
    group_set: "t.Optional[GroupSet]"
    #: The id of the AutoTest configuration connected to this assignment. This
    #: will always be given if there is a configuration connected to this
    #: assignment, even if you do not have permission to see the configuration
    #: itself.
    auto_test_id: "t.Optional[int]"
    #: Can you upload files to this assignment.
    files_upload_enabled: "bool"
    #: Can you connect git to this assignment.
    webhook_upload_enabled: "bool"
    #: Can you use the editor for this assignment.
    editor_upload_enabled: "bool"
    #: The maximum amount of submission a student may create, inclusive. The
    #: value `null` indicates that there is no limit.
    max_submissions: "t.Optional[int]"
    #: The time period in which a person can submit at most
    #: `amount_in_cool_off_period` amount.
    cool_off_period: "datetime.timedelta"
    #: The maximum amount of time a user can submit within
    #: `amount_in_cool_off_period`. This value is always \>= 0, if this value
    #: is 0 a user can submit an unlimited amount of time.
    amount_in_cool_off_period: "int"
    #: The moment reminder emails will be sent. This will be `None` if you
    #: don't have the permission to see this or if it is unset.
    reminder_time: "t.Optional[str]"
    #: The LMS providing this LTI assignment.
    lms_name: "t.Optional[str]"
    #: The peer feedback settings for this assignment. If `null` this
    #: assignment is not a peer feedback assignment.
    peer_feedback_settings: "t.Optional[AssignmentPeerFeedbackSettings]"
    #: The kind of reminder that will be sent. If you don't have the permission
    #: to see this it will always be `null`. If this is not set it will also be
    #: `null`.
    done_type: "t.Optional[str]"
    #: The email where the done email will be sent to. This will be `null` if
    #: you do not have permission to see this information.
    done_email: "t.Optional[str]"
    #: The assignment id of the assignment that determines the grader division
    #: of this assignment. This will be `null` if you do not have permissions
    #: to see this information, or if no such parent is set.
    division_parent_id: "t.Optional[int]"
    #: The ids of the analytics workspaces connected to this assignment.
    #: WARNING: This API is still in beta, and might change in the future.
    analytics_workspace_ids: "t.Sequence[int]"
    #: What kind of assignment is this.
    kind: "AssignmentKind"
    #: The anonymization algorithm used for this assignment.
    anonymized_grading: "t.Optional[AssignmentAnonymizationAlgo]"
    #: Optionally a glob for a file that should be loaded first in the file
    #: viewer. There is no guarantee that any file actually matches this glob.
    file_to_load_first: "t.Optional[str]"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "id",
                rqa.SimpleValue.int,
                doc="The id of the assignment.",
            ),
            rqa.RequiredArgument(
                "state",
                rqa.StringEnum("done", "grading", "hidden", "submitting"),
                doc="Current state of the assignment.",
            ),
            rqa.RequiredArgument(
                "description",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="Description of the assignment.",
            ),
            rqa.RequiredArgument(
                "created_at",
                rqa.RichValue.DateTime,
                doc="When this assignment was created.",
            ),
            rqa.RequiredArgument(
                "deadline",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The deadline of the assignment. It is possible the"
                    " assignment has no deadline yet, in which case it will be"
                    " `None`."
                ),
            ),
            rqa.RequiredArgument(
                "lock_date",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The moment this assignment locks, this can be seen as a"
                    " form of second deadline."
                ),
            ),
            rqa.RequiredArgument(
                "name",
                rqa.SimpleValue.str,
                doc="The name of the assignment.",
            ),
            rqa.RequiredArgument(
                "is_lti",
                rqa.SimpleValue.bool,
                doc="Is this an LTI assignment.",
            ),
            rqa.RequiredArgument(
                "course_id",
                rqa.SimpleValue.int,
                doc="Course of this assignment.",
            ),
            rqa.RequiredArgument(
                "cgignore",
                rqa.Nullable(
                    parsers.make_union(
                        parsers.ParserFor.make(SubmissionValidatorInputData),
                        rqa.SimpleValue.str,
                    )
                ),
                doc="The cginore.",
            ),
            rqa.RequiredArgument(
                "cgignore_version",
                rqa.Nullable(rqa.EnumValue(CGIgnoreVersion)),
                doc="The version of the cignore file.",
            ),
            rqa.RequiredArgument(
                "available_at",
                rqa.Nullable(rqa.RichValue.DateTime),
                doc=(
                    "The time the assignment will become available (i.e. the"
                    " state will switch from 'hidden' to 'open'). If the state"
                    " is not 'hidden' this value has no meaning. If this value"
                    " is not `None` you cannot change to state to 'hidden' or"
                    " 'open'."
                ),
            ),
            rqa.RequiredArgument(
                "send_login_links",
                rqa.SimpleValue.bool,
                doc=(
                    "Should we send login links to all users before the"
                    " `available_at` time."
                ),
            ),
            rqa.RequiredArgument(
                "fixed_max_rubric_points",
                rqa.Nullable(rqa.SimpleValue.float),
                doc=(
                    "The fixed value for the maximum that can be achieved in a"
                    " rubric. This can be higher and lower than the actual"
                    " max. Will be `None` if unset."
                ),
            ),
            rqa.RequiredArgument(
                "max_grade",
                rqa.Nullable(rqa.SimpleValue.float),
                doc=(
                    "The maximum grade you can get for this assignment. This"
                    " is based around the idea that a 10 is a 'perfect' score."
                    " So if this value is 12 a user can score 2 additional"
                    " bonus points. If this value is `None` it is unset and"
                    " regarded as a 10."
                ),
            ),
            rqa.RequiredArgument(
                "grading",
                parsers.ParserFor.make(AssignmentGradingSettingsAsJSON),
                doc=(
                    "Settings that influence how the grade for a submission"
                    " can be determined. TODO: Should we also move max\\_grade"
                    " and/or fixed\\_max\\_rubric\\_points to the grading"
                    " object?"
                ),
            ),
            rqa.RequiredArgument(
                "group_set",
                rqa.Nullable(parsers.ParserFor.make(GroupSet)),
                doc=(
                    "The group set of this assignment. This is `None` if this"
                    " assignment is not a group assignment."
                ),
            ),
            rqa.RequiredArgument(
                "auto_test_id",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The id of the AutoTest configuration connected to this"
                    " assignment. This will always be given if there is a"
                    " configuration connected to this assignment, even if you"
                    " do not have permission to see the configuration itself."
                ),
            ),
            rqa.RequiredArgument(
                "files_upload_enabled",
                rqa.SimpleValue.bool,
                doc="Can you upload files to this assignment.",
            ),
            rqa.RequiredArgument(
                "webhook_upload_enabled",
                rqa.SimpleValue.bool,
                doc="Can you connect git to this assignment.",
            ),
            rqa.RequiredArgument(
                "editor_upload_enabled",
                rqa.SimpleValue.bool,
                doc="Can you use the editor for this assignment.",
            ),
            rqa.RequiredArgument(
                "max_submissions",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The maximum amount of submission a student may create,"
                    " inclusive. The value `null` indicates that there is no"
                    " limit."
                ),
            ),
            rqa.RequiredArgument(
                "cool_off_period",
                rqa.RichValue.TimeDelta,
                doc=(
                    "The time period in which a person can submit at most"
                    " `amount_in_cool_off_period` amount."
                ),
            ),
            rqa.RequiredArgument(
                "amount_in_cool_off_period",
                rqa.SimpleValue.int,
                doc=(
                    "The maximum amount of time a user can submit within"
                    " `amount_in_cool_off_period`. This value is always \\>="
                    " 0, if this value is 0 a user can submit an unlimited"
                    " amount of time."
                ),
            ),
            rqa.RequiredArgument(
                "reminder_time",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The moment reminder emails will be sent. This will be"
                    " `None` if you don't have the permission to see this or"
                    " if it is unset."
                ),
            ),
            rqa.RequiredArgument(
                "lms_name",
                rqa.Nullable(rqa.SimpleValue.str),
                doc="The LMS providing this LTI assignment.",
            ),
            rqa.RequiredArgument(
                "peer_feedback_settings",
                rqa.Nullable(
                    parsers.ParserFor.make(AssignmentPeerFeedbackSettings)
                ),
                doc=(
                    "The peer feedback settings for this assignment. If `null`"
                    " this assignment is not a peer feedback assignment."
                ),
            ),
            rqa.RequiredArgument(
                "done_type",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The kind of reminder that will be sent. If you don't have"
                    " the permission to see this it will always be `null`. If"
                    " this is not set it will also be `null`."
                ),
            ),
            rqa.RequiredArgument(
                "done_email",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "The email where the done email will be sent to. This will"
                    " be `null` if you do not have permission to see this"
                    " information."
                ),
            ),
            rqa.RequiredArgument(
                "division_parent_id",
                rqa.Nullable(rqa.SimpleValue.int),
                doc=(
                    "The assignment id of the assignment that determines the"
                    " grader division of this assignment. This will be `null`"
                    " if you do not have permissions to see this information,"
                    " or if no such parent is set."
                ),
            ),
            rqa.RequiredArgument(
                "analytics_workspace_ids",
                rqa.List(rqa.SimpleValue.int),
                doc=(
                    "The ids of the analytics workspaces connected to this"
                    " assignment. WARNING: This API is still in beta, and"
                    " might change in the future."
                ),
            ),
            rqa.RequiredArgument(
                "kind",
                rqa.EnumValue(AssignmentKind),
                doc="What kind of assignment is this.",
            ),
            rqa.RequiredArgument(
                "anonymized_grading",
                rqa.Nullable(rqa.EnumValue(AssignmentAnonymizationAlgo)),
                doc="The anonymization algorithm used for this assignment.",
            ),
            rqa.RequiredArgument(
                "file_to_load_first",
                rqa.Nullable(rqa.SimpleValue.str),
                doc=(
                    "Optionally a glob for a file that should be loaded first"
                    " in the file viewer. There is no guarantee that any file"
                    " actually matches this glob."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "id": to_dict(self.id),
            "state": to_dict(self.state),
            "description": to_dict(self.description),
            "created_at": to_dict(self.created_at),
            "deadline": to_dict(self.deadline),
            "lock_date": to_dict(self.lock_date),
            "name": to_dict(self.name),
            "is_lti": to_dict(self.is_lti),
            "course_id": to_dict(self.course_id),
            "cgignore": to_dict(self.cgignore),
            "cgignore_version": to_dict(self.cgignore_version),
            "available_at": to_dict(self.available_at),
            "send_login_links": to_dict(self.send_login_links),
            "fixed_max_rubric_points": to_dict(self.fixed_max_rubric_points),
            "max_grade": to_dict(self.max_grade),
            "grading": to_dict(self.grading),
            "group_set": to_dict(self.group_set),
            "auto_test_id": to_dict(self.auto_test_id),
            "files_upload_enabled": to_dict(self.files_upload_enabled),
            "webhook_upload_enabled": to_dict(self.webhook_upload_enabled),
            "editor_upload_enabled": to_dict(self.editor_upload_enabled),
            "max_submissions": to_dict(self.max_submissions),
            "cool_off_period": to_dict(self.cool_off_period),
            "amount_in_cool_off_period": to_dict(
                self.amount_in_cool_off_period
            ),
            "reminder_time": to_dict(self.reminder_time),
            "lms_name": to_dict(self.lms_name),
            "peer_feedback_settings": to_dict(self.peer_feedback_settings),
            "done_type": to_dict(self.done_type),
            "done_email": to_dict(self.done_email),
            "division_parent_id": to_dict(self.division_parent_id),
            "analytics_workspace_ids": to_dict(self.analytics_workspace_ids),
            "kind": to_dict(self.kind),
            "anonymized_grading": to_dict(self.anonymized_grading),
            "file_to_load_first": to_dict(self.file_to_load_first),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["Assignment"], d: t.Dict[str, t.Any]
    ) -> "Assignment":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            id=parsed.id,
            state=parsed.state,
            description=parsed.description,
            created_at=parsed.created_at,
            deadline=parsed.deadline,
            lock_date=parsed.lock_date,
            name=parsed.name,
            is_lti=parsed.is_lti,
            course_id=parsed.course_id,
            cgignore=parsed.cgignore,
            cgignore_version=parsed.cgignore_version,
            available_at=parsed.available_at,
            send_login_links=parsed.send_login_links,
            fixed_max_rubric_points=parsed.fixed_max_rubric_points,
            max_grade=parsed.max_grade,
            grading=parsed.grading,
            group_set=parsed.group_set,
            auto_test_id=parsed.auto_test_id,
            files_upload_enabled=parsed.files_upload_enabled,
            webhook_upload_enabled=parsed.webhook_upload_enabled,
            editor_upload_enabled=parsed.editor_upload_enabled,
            max_submissions=parsed.max_submissions,
            cool_off_period=parsed.cool_off_period,
            amount_in_cool_off_period=parsed.amount_in_cool_off_period,
            reminder_time=parsed.reminder_time,
            lms_name=parsed.lms_name,
            peer_feedback_settings=parsed.peer_feedback_settings,
            done_type=parsed.done_type,
            done_email=parsed.done_email,
            division_parent_id=parsed.division_parent_id,
            analytics_workspace_ids=parsed.analytics_workspace_ids,
            kind=parsed.kind,
            anonymized_grading=parsed.anonymized_grading,
            file_to_load_first=parsed.file_to_load_first,
        )
        res.raw_data = d
        return res
