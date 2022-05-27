"""The module that defines the ``CoursePermMap`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict


@dataclass
class CoursePermMap:
    """The mapping between permission and value for a user."""

    #: Users with this permission can submit work to an assignment for other
    #: users. This means they can submit work that will have another user as
    #: the author.
    can_submit_others_work: "bool"
    #: Users with this permission can submit their work to assignments of this
    #: course. Usually only students have this permission.
    can_submit_own_work: "bool"
    #: Users with this permission can edit files in the submissions of this
    #: course. Usually TAs and teachers have this permission, so they can
    #: change files in the CodeGra.de filesystem if code doesn't compile, for
    #: example.
    can_edit_others_work: "bool"
    #: Users with this permission can grade submissions.
    can_grade_work: "bool"
    #: Users with this permission can see the grade for a submission before an
    #: assignment is set to "Done".
    can_see_grade_before_open: "bool"
    #: Users with this permission can see submissions of other users of this
    #: course.
    can_see_others_work: "bool"
    #: Users with this permission can view the assignments of this course.
    can_see_assignments: "bool"
    #: Users with this permission can view assignments of this course that are
    #: set to "Hidden".
    can_see_hidden_assignments: "bool"
    #: Users with this permission can update the assignment info such as name,
    #: deadline and status.
    can_edit_assignment_info: "bool"
    #: Users with this permission can assign a grader to submissions of
    #: assignments.
    can_assign_graders: "bool"
    #: Users with this permission can edit the .cgignore file for an
    #: assignment.
    can_edit_cgignore: "bool"
    #: Users with this permission can upload a zip file with submissions in the
    #: BlackBoard format.
    can_upload_bb_zip: "bool"
    #: Users with this permission can assign or remove permissions from course
    #: roles and add new course roles.
    can_edit_course_roles: "bool"
    #: Users with this permission can add users to this course and assign roles
    #: to those users.
    can_edit_course_users: "bool"
    #: Users with this permission can create new assignments for this course.
    can_create_assignment: "bool"
    #: Users with this permission can submit their work after the deadline of
    #: an assignment.
    can_upload_after_deadline: "bool"
    #: Users with this permission can see which grader is assigned to assess a
    #: submission.
    can_see_assignee: "bool"
    #: Users with this permission can update the rubrics for the assignments of
    #: this course.
    manage_rubrics: "bool"
    #: Users with this permission can view the teacher's revision of their
    #: submitted work.
    can_view_own_teacher_files: "bool"
    #: Users with this permission can see the grade history of an assignment.
    can_see_grade_history: "bool"
    #: Users with this permission can delete submissions.
    can_delete_submission: "bool"
    #: Users with this permission can change the status of graders for this
    #: course, whether they are done grading their assigned submissions or not.
    can_update_grader_status: "bool"
    #: Users with this permission can change the all notifications that are
    #: configured for this course. This includes when to send them and who to
    #: send them to.
    can_update_course_notifications: "bool"
    #: Users with this permission can edit the maximum grade possible, and
    #: therefore also determine if getting a 'bonus' for an assignment is also
    #: possible.
    can_edit_maximum_grade: "bool"
    #: Users with this permission can view the summary of a plagiarism check
    #: and see details of a plagiarism case. To view a plagiarism case between
    #: this and another course, the user must also have either this permission,
    #: or both "View assignments" and "View other's work" in the other course.
    can_view_plagiarism: "bool"
    #: Users with this permission can add and delete plagiarism runs.
    can_manage_plagiarism: "bool"
    #: Users with this permission can see all users of this course including
    #: the name of their role.
    can_list_course_users: "bool"
    #: Users with this permission can edit groups they are in. This means they
    #: can join groups, add users to groups they are in and change the name of
    #: groups they are in. They cannot remove users from groups they are in,
    #: except for themselves.
    can_edit_own_groups: "bool"
    #: Users with this permission can edit groups they are not in, they can add
    #: users, remove users and rename all groups. Users with this permission
    #: can also edit groups they are in.
    can_edit_others_groups: "bool"
    #: Users with this permission can edit groups which handed in a submission.
    #: Users with this permission cannot automatically edit groups, they also
    #: need either "Edit own groups" or "Edit others groups".
    can_edit_groups_after_submission: "bool"
    #: Users with this permission can view groups they are not in, and the
    #: members of these groups.
    can_view_others_groups: "bool"
    #: Users with this permission can change an assignment into a group
    #: assignment, and change the minimum and maximum required group size.
    can_edit_group_assignment: "bool"
    #: Users with this permissions can create, delete and edit group sets.
    can_edit_group_set: "bool"
    #: Users with this permission can create new groups in group assignments.
    can_create_groups: "bool"
    #: Users with this permission can see the snippets of this course, and use
    #: them while writing feedback.
    can_view_course_snippets: "bool"
    #: Users with this permission can create, edit, and delete snippets for
    #: this course.
    can_manage_course_snippets: "bool"
    #: Users with this permission can view hidden autotest fixtures.
    can_view_hidden_fixtures: "bool"
    #: Users with this permission can start AutoTest runs
    can_run_autotest: "bool"
    #: Users with this permission can delete AutoTest runs
    can_delete_autotest_run: "bool"
    #: Users with this permission can create, delete, edit the fixtures of,
    #: setup scripts of, and test sets of an AutoTest
    can_edit_autotest: "bool"
    #: Users with this permission can view hidden AutoTest steps if they have
    #: the permission to view the summary of this step
    can_view_hidden_autotest_steps: "bool"
    #: Users with this permission can view AutoTest, such as sets, before the
    #: state of the assignment is "Done"
    can_view_autotest_before_done: "bool"
    #: Users with this permission are allowed to see the details of non hidden
    #: AutoTest steps
    can_view_autotest_step_details: "bool"
    #: Users with this permission are allowed to see non hidden AutoTest
    #: fixtures
    can_view_autotest_fixture: "bool"
    #: Users with this permission can view output files created during an
    #: AutoTest before the assignment state is "Done"
    can_view_autotest_output_files_before_done: "bool"
    #: Users with this permission can delete assignments within this course.
    can_delete_assignments: "bool"
    #: Users with this permission can create new submissions, even if the
    #: maximum number of submissions has been reached, or if a cool-off period
    #: is in effect.
    can_override_submission_limiting: "bool"
    #: Users with this permission can see the output of linters before an
    #: assignment is set to "Done"
    can_see_linter_feedback_before_done: "bool"
    #: Users with this permission can see all inline and general feedback,
    #: except for peer feedback, before an assignment is set to "Done"
    can_see_user_feedback_before_done: "bool"
    #: Users with this permission can view the analytics dashboard of an
    #: assignment.
    can_view_analytics: "bool"
    #: Users with this permission can edit inline and general comments left by
    #: other users
    can_edit_others_comments: "bool"
    #: Users with this permission can add and reply to inline and general
    #: comments on submissions they are the author of
    can_add_own_inline_comments: "bool"
    #: Users with this permission may see the edit history of inline and
    #: general comments placed by others
    can_view_others_comment_edits: "bool"
    #: Users with this permission can view the author of inline and general
    #: feedback.
    can_view_feedback_author: "bool"
    #: Users with this permission can email students using the contact student
    #: button.
    can_email_students: "bool"
    #: Users with this permission can view unapproved inline and general
    #: comments, comments that need approval include peer feedback comments.
    #: Users still need to have the permission to see the feedback, so this
    #: permission alone is not enough to see peer feedback.
    can_view_inline_feedback_before_approved: "bool"
    #: Users with this permission can approve inline and general comments.
    #: Comments that need approval include peer feedback comments.
    can_approve_inline_comments: "bool"
    #: Users with this permission can edit the peer feedback status of an
    #: assignment.
    can_edit_peer_feedback_settings: "bool"
    #: Users with this permission will receive login links if this is enabled
    #: for the assignment. You should not give this permission to users with
    #: powerful permissions (such as "Can grade work").
    can_receive_login_links: "bool"
    #: Users with this permission can see a course that is archived. Users that
    #: do not have this permission will not be able to see any data (e.g.
    #: submissions) connected to an archived course.
    can_see_archived_courses: "bool"
    #: Users with this permission can archive courses. After archiving a course
    #: users that do not have the "View archived courses" permission will no
    #: longer be able too see the course.
    can_archive_courses: "bool"
    #: Users with this permission can edit general information of a course, for
    #: example the name.
    can_edit_course_info: "bool"
    #: Users with this permission can still submit their work after the lock
    #: date of an assignment.
    can_upload_after_lock_date: "bool"
    #: Users with this permission are allowed to see inline and general peer
    #: feedback before the state of an assignment has been set to "Done".
    can_see_peer_feedback_before_done: "bool"
    #: Users with this permission can see the real name of students even when
    #: anonymized grading is enabled.
    can_see_anonymized_names: "bool"
    #: Users with this permission can view AutoTest results of other users they
    #: are peer reviewing.
    can_view_peer_review_autotest_results: "bool"
    #: Users with this permission can submit their work for group assignments
    #: without being member of a group or when their group does not meet the
    #: minimum size requirements.
    can_upload_without_group: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.RequiredArgument(
                "can_submit_others_work",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can submit work to an"
                    " assignment for other users. This means they can submit"
                    " work that will have another user as the author."
                ),
            ),
            rqa.RequiredArgument(
                "can_submit_own_work",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can submit their work to"
                    " assignments of this course. Usually only students have"
                    " this permission."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_others_work",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit files in the"
                    " submissions of this course. Usually TAs and teachers"
                    " have this permission, so they can change files in the"
                    " CodeGra.de filesystem if code doesn't compile, for"
                    " example."
                ),
            ),
            rqa.RequiredArgument(
                "can_grade_work",
                rqa.SimpleValue.bool,
                doc="Users with this permission can grade submissions.",
            ),
            rqa.RequiredArgument(
                "can_see_grade_before_open",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see the grade for a"
                    ' submission before an assignment is set to "Done".'
                ),
            ),
            rqa.RequiredArgument(
                "can_see_others_work",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see submissions of other"
                    " users of this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_assignments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view the assignments of"
                    " this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_hidden_assignments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view assignments of this"
                    ' course that are set to "Hidden".'
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_assignment_info",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can update the assignment info"
                    " such as name, deadline and status."
                ),
            ),
            rqa.RequiredArgument(
                "can_assign_graders",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can assign a grader to"
                    " submissions of assignments."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_cgignore",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit the .cgignore file"
                    " for an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_upload_bb_zip",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can upload a zip file with"
                    " submissions in the BlackBoard format."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_course_roles",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can assign or remove"
                    " permissions from course roles and add new course roles."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_course_users",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can add users to this course"
                    " and assign roles to those users."
                ),
            ),
            rqa.RequiredArgument(
                "can_create_assignment",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can create new assignments for"
                    " this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_upload_after_deadline",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can submit their work after"
                    " the deadline of an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_assignee",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see which grader is"
                    " assigned to assess a submission."
                ),
            ),
            rqa.RequiredArgument(
                "manage_rubrics",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can update the rubrics for the"
                    " assignments of this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_own_teacher_files",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view the teacher's"
                    " revision of their submitted work."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_grade_history",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see the grade history of"
                    " an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_delete_submission",
                rqa.SimpleValue.bool,
                doc="Users with this permission can delete submissions.",
            ),
            rqa.RequiredArgument(
                "can_update_grader_status",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can change the status of"
                    " graders for this course, whether they are done grading"
                    " their assigned submissions or not."
                ),
            ),
            rqa.RequiredArgument(
                "can_update_course_notifications",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can change the all"
                    " notifications that are configured for this course. This"
                    " includes when to send them and who to send them to."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_maximum_grade",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit the maximum grade"
                    " possible, and therefore also determine if getting a"
                    " 'bonus' for an assignment is also possible."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_plagiarism",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view the summary of a"
                    " plagiarism check and see details of a plagiarism case."
                    " To view a plagiarism case between this and another"
                    " course, the user must also have either this permission,"
                    ' or both "View assignments" and "View other\'s work" in'
                    " the other course."
                ),
            ),
            rqa.RequiredArgument(
                "can_manage_plagiarism",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can add and delete plagiarism"
                    " runs."
                ),
            ),
            rqa.RequiredArgument(
                "can_list_course_users",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see all users of this"
                    " course including the name of their role."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_own_groups",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit groups they are in."
                    " This means they can join groups, add users to groups"
                    " they are in and change the name of groups they are in."
                    " They cannot remove users from groups they are in, except"
                    " for themselves."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_others_groups",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit groups they are not"
                    " in, they can add users, remove users and rename all"
                    " groups. Users with this permission can also edit groups"
                    " they are in."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_groups_after_submission",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit groups which handed"
                    " in a submission. Users with this permission cannot"
                    ' automatically edit groups, they also need either "Edit'
                    ' own groups" or "Edit others groups".'
                ),
            ),
            rqa.RequiredArgument(
                "can_view_others_groups",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view groups they are not"
                    " in, and the members of these groups."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_group_assignment",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can change an assignment into"
                    " a group assignment, and change the minimum and maximum"
                    " required group size."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_group_set",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permissions can create, delete and edit"
                    " group sets."
                ),
            ),
            rqa.RequiredArgument(
                "can_create_groups",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can create new groups in group"
                    " assignments."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_course_snippets",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see the snippets of this"
                    " course, and use them while writing feedback."
                ),
            ),
            rqa.RequiredArgument(
                "can_manage_course_snippets",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can create, edit, and delete"
                    " snippets for this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_hidden_fixtures",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view hidden autotest"
                    " fixtures."
                ),
            ),
            rqa.RequiredArgument(
                "can_run_autotest",
                rqa.SimpleValue.bool,
                doc="Users with this permission can start AutoTest runs",
            ),
            rqa.RequiredArgument(
                "can_delete_autotest_run",
                rqa.SimpleValue.bool,
                doc="Users with this permission can delete AutoTest runs",
            ),
            rqa.RequiredArgument(
                "can_edit_autotest",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can create, delete, edit the"
                    " fixtures of, setup scripts of, and test sets of an"
                    " AutoTest"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_hidden_autotest_steps",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view hidden AutoTest steps"
                    " if they have the permission to view the summary of this"
                    " step"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_autotest_before_done",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view AutoTest, such as"
                    ' sets, before the state of the assignment is "Done"'
                ),
            ),
            rqa.RequiredArgument(
                "can_view_autotest_step_details",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission are allowed to see the details"
                    " of non hidden AutoTest steps"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_autotest_fixture",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission are allowed to see non hidden"
                    " AutoTest fixtures"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_autotest_output_files_before_done",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view output files created"
                    ' during an AutoTest before the assignment state is "Done"'
                ),
            ),
            rqa.RequiredArgument(
                "can_delete_assignments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can delete assignments within"
                    " this course."
                ),
            ),
            rqa.RequiredArgument(
                "can_override_submission_limiting",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can create new submissions,"
                    " even if the maximum number of submissions has been"
                    " reached, or if a cool-off period is in effect."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_linter_feedback_before_done",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see the output of linters"
                    ' before an assignment is set to "Done"'
                ),
            ),
            rqa.RequiredArgument(
                "can_see_user_feedback_before_done",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see all inline and general"
                    " feedback, except for peer feedback, before an assignment"
                    ' is set to "Done"'
                ),
            ),
            rqa.RequiredArgument(
                "can_view_analytics",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view the analytics"
                    " dashboard of an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_others_comments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit inline and general"
                    " comments left by other users"
                ),
            ),
            rqa.RequiredArgument(
                "can_add_own_inline_comments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can add and reply to inline"
                    " and general comments on submissions they are the"
                    " author of"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_others_comment_edits",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission may see the edit history of"
                    " inline and general comments placed by others"
                ),
            ),
            rqa.RequiredArgument(
                "can_view_feedback_author",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view the author of inline"
                    " and general feedback."
                ),
            ),
            rqa.RequiredArgument(
                "can_email_students",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can email students using the"
                    " contact student button."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_inline_feedback_before_approved",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view unapproved inline and"
                    " general comments, comments that need approval include"
                    " peer feedback comments. Users still need to have the"
                    " permission to see the feedback, so this permission alone"
                    " is not enough to see peer feedback."
                ),
            ),
            rqa.RequiredArgument(
                "can_approve_inline_comments",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can approve inline and general"
                    " comments. Comments that need approval include peer"
                    " feedback comments."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_peer_feedback_settings",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit the peer feedback"
                    " status of an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_receive_login_links",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission will receive login links if"
                    " this is enabled for the assignment. You should not give"
                    " this permission to users with powerful permissions (such"
                    ' as "Can grade work").'
                ),
            ),
            rqa.RequiredArgument(
                "can_see_archived_courses",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see a course that is"
                    " archived. Users that do not have this permission will"
                    " not be able to see any data (e.g. submissions) connected"
                    " to an archived course."
                ),
            ),
            rqa.RequiredArgument(
                "can_archive_courses",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can archive courses. After"
                    ' archiving a course users that do not have the "View'
                    ' archived courses" permission will no longer be able too'
                    " see the course."
                ),
            ),
            rqa.RequiredArgument(
                "can_edit_course_info",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can edit general information"
                    " of a course, for example the name."
                ),
            ),
            rqa.RequiredArgument(
                "can_upload_after_lock_date",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can still submit their work"
                    " after the lock date of an assignment."
                ),
            ),
            rqa.RequiredArgument(
                "can_see_peer_feedback_before_done",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission are allowed to see inline and"
                    " general peer feedback before the state of an assignment"
                    ' has been set to "Done".'
                ),
            ),
            rqa.RequiredArgument(
                "can_see_anonymized_names",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can see the real name of"
                    " students even when anonymized grading is enabled."
                ),
            ),
            rqa.RequiredArgument(
                "can_view_peer_review_autotest_results",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can view AutoTest results of"
                    " other users they are peer reviewing."
                ),
            ),
            rqa.RequiredArgument(
                "can_upload_without_group",
                rqa.SimpleValue.bool,
                doc=(
                    "Users with this permission can submit their work for"
                    " group assignments without being member of a group or"
                    " when their group does not meet the minimum size"
                    " requirements."
                ),
            ),
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "can_submit_others_work": to_dict(self.can_submit_others_work),
            "can_submit_own_work": to_dict(self.can_submit_own_work),
            "can_edit_others_work": to_dict(self.can_edit_others_work),
            "can_grade_work": to_dict(self.can_grade_work),
            "can_see_grade_before_open": to_dict(
                self.can_see_grade_before_open
            ),
            "can_see_others_work": to_dict(self.can_see_others_work),
            "can_see_assignments": to_dict(self.can_see_assignments),
            "can_see_hidden_assignments": to_dict(
                self.can_see_hidden_assignments
            ),
            "can_edit_assignment_info": to_dict(self.can_edit_assignment_info),
            "can_assign_graders": to_dict(self.can_assign_graders),
            "can_edit_cgignore": to_dict(self.can_edit_cgignore),
            "can_upload_bb_zip": to_dict(self.can_upload_bb_zip),
            "can_edit_course_roles": to_dict(self.can_edit_course_roles),
            "can_edit_course_users": to_dict(self.can_edit_course_users),
            "can_create_assignment": to_dict(self.can_create_assignment),
            "can_upload_after_deadline": to_dict(
                self.can_upload_after_deadline
            ),
            "can_see_assignee": to_dict(self.can_see_assignee),
            "manage_rubrics": to_dict(self.manage_rubrics),
            "can_view_own_teacher_files": to_dict(
                self.can_view_own_teacher_files
            ),
            "can_see_grade_history": to_dict(self.can_see_grade_history),
            "can_delete_submission": to_dict(self.can_delete_submission),
            "can_update_grader_status": to_dict(self.can_update_grader_status),
            "can_update_course_notifications": to_dict(
                self.can_update_course_notifications
            ),
            "can_edit_maximum_grade": to_dict(self.can_edit_maximum_grade),
            "can_view_plagiarism": to_dict(self.can_view_plagiarism),
            "can_manage_plagiarism": to_dict(self.can_manage_plagiarism),
            "can_list_course_users": to_dict(self.can_list_course_users),
            "can_edit_own_groups": to_dict(self.can_edit_own_groups),
            "can_edit_others_groups": to_dict(self.can_edit_others_groups),
            "can_edit_groups_after_submission": to_dict(
                self.can_edit_groups_after_submission
            ),
            "can_view_others_groups": to_dict(self.can_view_others_groups),
            "can_edit_group_assignment": to_dict(
                self.can_edit_group_assignment
            ),
            "can_edit_group_set": to_dict(self.can_edit_group_set),
            "can_create_groups": to_dict(self.can_create_groups),
            "can_view_course_snippets": to_dict(self.can_view_course_snippets),
            "can_manage_course_snippets": to_dict(
                self.can_manage_course_snippets
            ),
            "can_view_hidden_fixtures": to_dict(self.can_view_hidden_fixtures),
            "can_run_autotest": to_dict(self.can_run_autotest),
            "can_delete_autotest_run": to_dict(self.can_delete_autotest_run),
            "can_edit_autotest": to_dict(self.can_edit_autotest),
            "can_view_hidden_autotest_steps": to_dict(
                self.can_view_hidden_autotest_steps
            ),
            "can_view_autotest_before_done": to_dict(
                self.can_view_autotest_before_done
            ),
            "can_view_autotest_step_details": to_dict(
                self.can_view_autotest_step_details
            ),
            "can_view_autotest_fixture": to_dict(
                self.can_view_autotest_fixture
            ),
            "can_view_autotest_output_files_before_done": to_dict(
                self.can_view_autotest_output_files_before_done
            ),
            "can_delete_assignments": to_dict(self.can_delete_assignments),
            "can_override_submission_limiting": to_dict(
                self.can_override_submission_limiting
            ),
            "can_see_linter_feedback_before_done": to_dict(
                self.can_see_linter_feedback_before_done
            ),
            "can_see_user_feedback_before_done": to_dict(
                self.can_see_user_feedback_before_done
            ),
            "can_view_analytics": to_dict(self.can_view_analytics),
            "can_edit_others_comments": to_dict(self.can_edit_others_comments),
            "can_add_own_inline_comments": to_dict(
                self.can_add_own_inline_comments
            ),
            "can_view_others_comment_edits": to_dict(
                self.can_view_others_comment_edits
            ),
            "can_view_feedback_author": to_dict(self.can_view_feedback_author),
            "can_email_students": to_dict(self.can_email_students),
            "can_view_inline_feedback_before_approved": to_dict(
                self.can_view_inline_feedback_before_approved
            ),
            "can_approve_inline_comments": to_dict(
                self.can_approve_inline_comments
            ),
            "can_edit_peer_feedback_settings": to_dict(
                self.can_edit_peer_feedback_settings
            ),
            "can_receive_login_links": to_dict(self.can_receive_login_links),
            "can_see_archived_courses": to_dict(self.can_see_archived_courses),
            "can_archive_courses": to_dict(self.can_archive_courses),
            "can_edit_course_info": to_dict(self.can_edit_course_info),
            "can_upload_after_lock_date": to_dict(
                self.can_upload_after_lock_date
            ),
            "can_see_peer_feedback_before_done": to_dict(
                self.can_see_peer_feedback_before_done
            ),
            "can_see_anonymized_names": to_dict(self.can_see_anonymized_names),
            "can_view_peer_review_autotest_results": to_dict(
                self.can_view_peer_review_autotest_results
            ),
            "can_upload_without_group": to_dict(self.can_upload_without_group),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["CoursePermMap"], d: t.Dict[str, t.Any]
    ) -> "CoursePermMap":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            can_submit_others_work=parsed.can_submit_others_work,
            can_submit_own_work=parsed.can_submit_own_work,
            can_edit_others_work=parsed.can_edit_others_work,
            can_grade_work=parsed.can_grade_work,
            can_see_grade_before_open=parsed.can_see_grade_before_open,
            can_see_others_work=parsed.can_see_others_work,
            can_see_assignments=parsed.can_see_assignments,
            can_see_hidden_assignments=parsed.can_see_hidden_assignments,
            can_edit_assignment_info=parsed.can_edit_assignment_info,
            can_assign_graders=parsed.can_assign_graders,
            can_edit_cgignore=parsed.can_edit_cgignore,
            can_upload_bb_zip=parsed.can_upload_bb_zip,
            can_edit_course_roles=parsed.can_edit_course_roles,
            can_edit_course_users=parsed.can_edit_course_users,
            can_create_assignment=parsed.can_create_assignment,
            can_upload_after_deadline=parsed.can_upload_after_deadline,
            can_see_assignee=parsed.can_see_assignee,
            manage_rubrics=parsed.manage_rubrics,
            can_view_own_teacher_files=parsed.can_view_own_teacher_files,
            can_see_grade_history=parsed.can_see_grade_history,
            can_delete_submission=parsed.can_delete_submission,
            can_update_grader_status=parsed.can_update_grader_status,
            can_update_course_notifications=parsed.can_update_course_notifications,
            can_edit_maximum_grade=parsed.can_edit_maximum_grade,
            can_view_plagiarism=parsed.can_view_plagiarism,
            can_manage_plagiarism=parsed.can_manage_plagiarism,
            can_list_course_users=parsed.can_list_course_users,
            can_edit_own_groups=parsed.can_edit_own_groups,
            can_edit_others_groups=parsed.can_edit_others_groups,
            can_edit_groups_after_submission=parsed.can_edit_groups_after_submission,
            can_view_others_groups=parsed.can_view_others_groups,
            can_edit_group_assignment=parsed.can_edit_group_assignment,
            can_edit_group_set=parsed.can_edit_group_set,
            can_create_groups=parsed.can_create_groups,
            can_view_course_snippets=parsed.can_view_course_snippets,
            can_manage_course_snippets=parsed.can_manage_course_snippets,
            can_view_hidden_fixtures=parsed.can_view_hidden_fixtures,
            can_run_autotest=parsed.can_run_autotest,
            can_delete_autotest_run=parsed.can_delete_autotest_run,
            can_edit_autotest=parsed.can_edit_autotest,
            can_view_hidden_autotest_steps=parsed.can_view_hidden_autotest_steps,
            can_view_autotest_before_done=parsed.can_view_autotest_before_done,
            can_view_autotest_step_details=parsed.can_view_autotest_step_details,
            can_view_autotest_fixture=parsed.can_view_autotest_fixture,
            can_view_autotest_output_files_before_done=parsed.can_view_autotest_output_files_before_done,
            can_delete_assignments=parsed.can_delete_assignments,
            can_override_submission_limiting=parsed.can_override_submission_limiting,
            can_see_linter_feedback_before_done=parsed.can_see_linter_feedback_before_done,
            can_see_user_feedback_before_done=parsed.can_see_user_feedback_before_done,
            can_view_analytics=parsed.can_view_analytics,
            can_edit_others_comments=parsed.can_edit_others_comments,
            can_add_own_inline_comments=parsed.can_add_own_inline_comments,
            can_view_others_comment_edits=parsed.can_view_others_comment_edits,
            can_view_feedback_author=parsed.can_view_feedback_author,
            can_email_students=parsed.can_email_students,
            can_view_inline_feedback_before_approved=parsed.can_view_inline_feedback_before_approved,
            can_approve_inline_comments=parsed.can_approve_inline_comments,
            can_edit_peer_feedback_settings=parsed.can_edit_peer_feedback_settings,
            can_receive_login_links=parsed.can_receive_login_links,
            can_see_archived_courses=parsed.can_see_archived_courses,
            can_archive_courses=parsed.can_archive_courses,
            can_edit_course_info=parsed.can_edit_course_info,
            can_upload_after_lock_date=parsed.can_upload_after_lock_date,
            can_see_peer_feedback_before_done=parsed.can_see_peer_feedback_before_done,
            can_see_anonymized_names=parsed.can_see_anonymized_names,
            can_view_peer_review_autotest_results=parsed.can_view_peer_review_autotest_results,
            can_upload_without_group=parsed.can_upload_without_group,
        )
        res.raw_data = d
        return res
