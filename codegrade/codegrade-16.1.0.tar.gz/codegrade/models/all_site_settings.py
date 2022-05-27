"""The module that defines the ``AllSiteSettings`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import datetime
import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa

from ..utils import to_dict
from .frontend_site_settings import FrontendSiteSettings


@dataclass
class AllSiteSettings(FrontendSiteSettings):
    """The JSON representation of all options."""

    #: The amount of time there can be between two heartbeats of a runner.
    #: Changing this to a lower value might cause some runners to crash.
    auto_test_heartbeat_interval: "datetime.timedelta"
    #: The max amount of heartbeats that we may miss from a runner before we
    #: kill it and start a new one.
    auto_test_heartbeat_max_missed: "int"
    #: This value determines the amount of runners we request for a single
    #: assignment. The amount of runners requested is equal to the amount of
    #: students not yet started divided by this value.
    auto_test_max_jobs_per_runner: "int"
    #: The maximum amount of batch AutoTest runs we will do at a time. AutoTest
    #: batch runs are runs that are done after the deadline for configurations
    #: that have hidden tests. Increasing this variable might cause heavy
    #: server load.
    auto_test_max_concurrent_batch_runs: "int"
    #: The maximum amount of time a result can be in the "not started" state
    #: before we raise an alarm on the about health page.
    auto_test_max_result_not_started: "datetime.timedelta"
    #: The maximum size of metadata stored on a unit test step.
    auto_test_max_unit_test_metadata_length: "int"
    #: The minimum strength passwords by users should have. The higher this
    #: value the stronger the password should be. When increasing the strength
    #: all users with too weak passwords will be shown a warning on the next
    #: login.
    min_password_score: "int"
    #: The amount of time a reset token is valid. You should not increase this
    #: value too much as users might be not be too careful with these tokens.
    #: Increasing this value will allow **all** existing tokens to live longer.
    reset_token_time: "datetime.timedelta"
    #: The amount of time the link send in notification emails to change the
    #: notification preferences works to actually change the notifications.
    setting_token_time: "datetime.timedelta"
    #: The maximum amount of files and directories allowed in a single archive.
    max_number_of_files: "int"
    #: The maximum size of uploaded files that are mostly uploaded by "trusted"
    #: users. Examples of these kind of files include AutoTest fixtures and
    #: plagiarism base code.
    max_large_upload_size: "int"
    #: The maximum total size of uploaded files that are uploaded by normal
    #: users. This is also the maximum total size of submissions. Increasing
    #: this size might cause a hosting costs to increase.
    max_normal_upload_size: "int"
    #: The maximum total size of files part of an editor submission in
    #: dynamodb. This is not the same as MAX\_NORMAL\_UPLOAD\_SIZE. Increasing
    #: this size might cause a hosting costs to increase.
    max_dynamo_submission_size: "int"
    #: The maximum size of a single file uploaded by normal users. This limit
    #: is really here to prevent users from uploading extremely large files
    #: which can't really be downloaded/shown anyway.
    max_file_size: "int"
    #: The maximum size of a single file's updates in dynamodb. This is not the
    #: same as MAX\_FILE\_SIZE. This limit is to avoid having huge files stored
    #: in dynamodb, as storage is expensive.
    max_dynamo_file_size: "int"
    #: The maximum size of a single update (CRDT) to a file in dynamodb. This
    #: is not the same as MAX\_DYNAMO\_FILE\_SIZE, as it refers to a single
    #: edit operation. This limit is to avoid having huge items stored in
    #: dynamodb, as storage is expensive. If the CRDT exceeds the given size,
    #: it will be uploaded to a S3 object.
    max_document_update_size: "int"
    #: The time a login session is valid. After this amount of time a user will
    #: always need to re-authenticate.
    jwt_access_token_expires: "datetime.timedelta"
    #: The time a user has to download a file from the mirror storage, after
    #: this time the file will be deleted.
    max_mirror_file_age: "datetime.timedelta"
    #: The maximum number of user settings stored per user.
    max_user_setting_amount: "int"
    #: Should a registration email be sent to new users upon registration.
    send_registration_email: "bool"

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: FrontendSiteSettings.data_parser.parser.combine(
            rqa.FixedMapping(
                rqa.RequiredArgument(
                    "AUTO_TEST_HEARTBEAT_INTERVAL",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The amount of time there can be between two"
                        " heartbeats of a runner. Changing this to a lower"
                        " value might cause some runners to crash."
                    ),
                ),
                rqa.RequiredArgument(
                    "AUTO_TEST_HEARTBEAT_MAX_MISSED",
                    rqa.SimpleValue.int,
                    doc=(
                        "The max amount of heartbeats that we may miss from a"
                        " runner before we kill it and start a new one."
                    ),
                ),
                rqa.RequiredArgument(
                    "AUTO_TEST_MAX_JOBS_PER_RUNNER",
                    rqa.SimpleValue.int,
                    doc=(
                        "This value determines the amount of runners we"
                        " request for a single assignment. The amount of"
                        " runners requested is equal to the amount of students"
                        " not yet started divided by this value."
                    ),
                ),
                rqa.RequiredArgument(
                    "AUTO_TEST_MAX_CONCURRENT_BATCH_RUNS",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum amount of batch AutoTest runs we will do"
                        " at a time. AutoTest batch runs are runs that are"
                        " done after the deadline for configurations that have"
                        " hidden tests. Increasing this variable might cause"
                        " heavy server load."
                    ),
                ),
                rqa.RequiredArgument(
                    "AUTO_TEST_MAX_RESULT_NOT_STARTED",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The maximum amount of time a result can be in the"
                        ' "not started" state before we raise an alarm on the'
                        " about health page."
                    ),
                ),
                rqa.RequiredArgument(
                    "AUTO_TEST_MAX_UNIT_TEST_METADATA_LENGTH",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum size of metadata stored on a unit test"
                        " step."
                    ),
                ),
                rqa.RequiredArgument(
                    "MIN_PASSWORD_SCORE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The minimum strength passwords by users should have."
                        " The higher this value the stronger the password"
                        " should be. When increasing the strength all users"
                        " with too weak passwords will be shown a warning on"
                        " the next login."
                    ),
                ),
                rqa.RequiredArgument(
                    "RESET_TOKEN_TIME",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The amount of time a reset token is valid. You should"
                        " not increase this value too much as users might be"
                        " not be too careful with these tokens. Increasing"
                        " this value will allow **all** existing tokens to"
                        " live longer."
                    ),
                ),
                rqa.RequiredArgument(
                    "SETTING_TOKEN_TIME",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The amount of time the link send in notification"
                        " emails to change the notification preferences works"
                        " to actually change the notifications."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_NUMBER_OF_FILES",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum amount of files and directories allowed"
                        " in a single archive."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_LARGE_UPLOAD_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum size of uploaded files that are mostly"
                        ' uploaded by "trusted" users. Examples of these kind'
                        " of files include AutoTest fixtures and plagiarism"
                        " base code."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_NORMAL_UPLOAD_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum total size of uploaded files that are"
                        " uploaded by normal users. This is also the maximum"
                        " total size of submissions. Increasing this size"
                        " might cause a hosting costs to increase."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_DYNAMO_SUBMISSION_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum total size of files part of an editor"
                        " submission in dynamodb. This is not the same as"
                        " MAX\\_NORMAL\\_UPLOAD\\_SIZE. Increasing this size"
                        " might cause a hosting costs to increase."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_FILE_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum size of a single file uploaded by normal"
                        " users. This limit is really here to prevent users"
                        " from uploading extremely large files which can't"
                        " really be downloaded/shown anyway."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_DYNAMO_FILE_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum size of a single file's updates in"
                        " dynamodb. This is not the same as MAX\\_FILE\\_SIZE."
                        " This limit is to avoid having huge files stored in"
                        " dynamodb, as storage is expensive."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_DOCUMENT_UPDATE_SIZE",
                    rqa.SimpleValue.int,
                    doc=(
                        "The maximum size of a single update (CRDT) to a file"
                        " in dynamodb. This is not the same as"
                        " MAX\\_DYNAMO\\_FILE\\_SIZE, as it refers to a single"
                        " edit operation. This limit is to avoid having huge"
                        " items stored in dynamodb, as storage is expensive."
                        " If the CRDT exceeds the given size, it will be"
                        " uploaded to a S3 object."
                    ),
                ),
                rqa.RequiredArgument(
                    "JWT_ACCESS_TOKEN_EXPIRES",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The time a login session is valid. After this amount"
                        " of time a user will always need to re-authenticate."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_MIRROR_FILE_AGE",
                    rqa.RichValue.TimeDelta,
                    doc=(
                        "The time a user has to download a file from the"
                        " mirror storage, after this time the file will be"
                        " deleted."
                    ),
                ),
                rqa.RequiredArgument(
                    "MAX_USER_SETTING_AMOUNT",
                    rqa.SimpleValue.int,
                    doc="The maximum number of user settings stored per user.",
                ),
                rqa.RequiredArgument(
                    "SEND_REGISTRATION_EMAIL",
                    rqa.SimpleValue.bool,
                    doc=(
                        "Should a registration email be sent to new users upon"
                        " registration."
                    ),
                ),
            )
        ).use_readable_describe(True)
    )

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {
            "AUTO_TEST_HEARTBEAT_INTERVAL": to_dict(
                self.auto_test_heartbeat_interval
            ),
            "AUTO_TEST_HEARTBEAT_MAX_MISSED": to_dict(
                self.auto_test_heartbeat_max_missed
            ),
            "AUTO_TEST_MAX_JOBS_PER_RUNNER": to_dict(
                self.auto_test_max_jobs_per_runner
            ),
            "AUTO_TEST_MAX_CONCURRENT_BATCH_RUNS": to_dict(
                self.auto_test_max_concurrent_batch_runs
            ),
            "AUTO_TEST_MAX_RESULT_NOT_STARTED": to_dict(
                self.auto_test_max_result_not_started
            ),
            "AUTO_TEST_MAX_UNIT_TEST_METADATA_LENGTH": to_dict(
                self.auto_test_max_unit_test_metadata_length
            ),
            "MIN_PASSWORD_SCORE": to_dict(self.min_password_score),
            "RESET_TOKEN_TIME": to_dict(self.reset_token_time),
            "SETTING_TOKEN_TIME": to_dict(self.setting_token_time),
            "MAX_NUMBER_OF_FILES": to_dict(self.max_number_of_files),
            "MAX_LARGE_UPLOAD_SIZE": to_dict(self.max_large_upload_size),
            "MAX_NORMAL_UPLOAD_SIZE": to_dict(self.max_normal_upload_size),
            "MAX_DYNAMO_SUBMISSION_SIZE": to_dict(
                self.max_dynamo_submission_size
            ),
            "MAX_FILE_SIZE": to_dict(self.max_file_size),
            "MAX_DYNAMO_FILE_SIZE": to_dict(self.max_dynamo_file_size),
            "MAX_DOCUMENT_UPDATE_SIZE": to_dict(self.max_document_update_size),
            "JWT_ACCESS_TOKEN_EXPIRES": to_dict(self.jwt_access_token_expires),
            "MAX_MIRROR_FILE_AGE": to_dict(self.max_mirror_file_age),
            "MAX_USER_SETTING_AMOUNT": to_dict(self.max_user_setting_amount),
            "SEND_REGISTRATION_EMAIL": to_dict(self.send_registration_email),
            "AUTO_TEST_MAX_TIME_COMMAND": to_dict(
                self.auto_test_max_time_command
            ),
            "AUTO_TEST_IO_TEST_MESSAGE": to_dict(
                self.auto_test_io_test_message
            ),
            "AUTO_TEST_IO_TEST_SUB_MESSAGE": to_dict(
                self.auto_test_io_test_sub_message
            ),
            "AUTO_TEST_RUN_PROGRAM_MESSAGE": to_dict(
                self.auto_test_run_program_message
            ),
            "AUTO_TEST_CAPTURE_POINTS_MESSAGE": to_dict(
                self.auto_test_capture_points_message
            ),
            "AUTO_TEST_CHECKPOINT_MESSAGE": to_dict(
                self.auto_test_checkpoint_message
            ),
            "AUTO_TEST_UNIT_TEST_MESSAGE": to_dict(
                self.auto_test_unit_test_message
            ),
            "AUTO_TEST_CODE_QUALITY_MESSAGE": to_dict(
                self.auto_test_code_quality_message
            ),
            "EXAM_LOGIN_MAX_LENGTH": to_dict(self.exam_login_max_length),
            "LOGIN_TOKEN_BEFORE_TIME": to_dict(self.login_token_before_time),
            "SITE_EMAIL": to_dict(self.site_email),
            "MAX_LINES": to_dict(self.max_lines),
            "NOTIFICATION_POLL_TIME": to_dict(self.notification_poll_time),
            "RELEASE_MESSAGE_MAX_TIME": to_dict(self.release_message_max_time),
            "MAX_PLAGIARISM_MATCHES": to_dict(self.max_plagiarism_matches),
            "AUTO_TEST_MAX_GLOBAL_SETUP_TIME": to_dict(
                self.auto_test_max_global_setup_time
            ),
            "AUTO_TEST_MAX_PER_STUDENT_SETUP_TIME": to_dict(
                self.auto_test_max_per_student_setup_time
            ),
            "ASSIGNMENT_DEFAULT_GRADING_SCALE": to_dict(
                self.assignment_default_grading_scale
            ),
            "BLACKBOARD_ZIP_UPLOAD_ENABLED": to_dict(
                self.blackboard_zip_upload_enabled
            ),
            "RUBRICS_ENABLED": to_dict(self.rubrics_enabled),
            "AUTOMATIC_LTI_ROLE_ENABLED": to_dict(
                self.automatic_lti_role_enabled
            ),
            "LTI_ENABLED": to_dict(self.lti_enabled),
            "LINTERS_ENABLED": to_dict(self.linters_enabled),
            "INCREMENTAL_RUBRIC_SUBMISSION_ENABLED": to_dict(
                self.incremental_rubric_submission_enabled
            ),
            "REGISTER_ENABLED": to_dict(self.register_enabled),
            "GROUPS_ENABLED": to_dict(self.groups_enabled),
            "AUTO_TEST_ENABLED": to_dict(self.auto_test_enabled),
            "COURSE_REGISTER_ENABLED": to_dict(self.course_register_enabled),
            "RENDER_HTML_ENABLED": to_dict(self.render_html_enabled),
            "EMAIL_STUDENTS_ENABLED": to_dict(self.email_students_enabled),
            "PEER_FEEDBACK_ENABLED": to_dict(self.peer_feedback_enabled),
            "AT_IMAGE_CACHING_ENABLED": to_dict(self.at_image_caching_enabled),
            "STUDENT_PAYMENT_ENABLED": to_dict(self.student_payment_enabled),
            "EDITOR_ENABLED": to_dict(self.editor_enabled),
            "SERVER_TIME_CORRECTION_ENABLED": to_dict(
                self.server_time_correction_enabled
            ),
            "METRIC_GATHERING_ENABLED": to_dict(self.metric_gathering_enabled),
            "GRADING_NOTIFICATIONS_ENABLED": to_dict(
                self.grading_notifications_enabled
            ),
            "FEEDBACK_THREADS_INITIALLY_COLLAPSED": to_dict(
                self.feedback_threads_initially_collapsed
            ),
            "METRIC_GATHERING_TIME_INTERVAL": to_dict(
                self.metric_gathering_time_interval
            ),
            "METRIC_GATHERING_EVENT_INTERVAL": to_dict(
                self.metric_gathering_event_interval
            ),
            "METRIC_EVENT_BUFFER_SIZE": to_dict(self.metric_event_buffer_size),
            "METRIC_EVALUATION_TIME_LIMIT": to_dict(
                self.metric_evaluation_time_limit
            ),
            "METRIC_EVALUATION_TIME_CHUNK_SIZE": to_dict(
                self.metric_evaluation_time_chunk_size
            ),
            "METRIC_GATHERING_EXPRESSIONS": to_dict(
                self.metric_gathering_expressions
            ),
            "SERVER_TIME_DIFF_TOLERANCE": to_dict(
                self.server_time_diff_tolerance
            ),
            "SERVER_TIME_SYNC_INTERVAL": to_dict(
                self.server_time_sync_interval
            ),
        }
        return res

    @classmethod
    def from_dict(
        cls: t.Type["AllSiteSettings"], d: t.Dict[str, t.Any]
    ) -> "AllSiteSettings":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            auto_test_heartbeat_interval=parsed.AUTO_TEST_HEARTBEAT_INTERVAL,
            auto_test_heartbeat_max_missed=parsed.AUTO_TEST_HEARTBEAT_MAX_MISSED,
            auto_test_max_jobs_per_runner=parsed.AUTO_TEST_MAX_JOBS_PER_RUNNER,
            auto_test_max_concurrent_batch_runs=parsed.AUTO_TEST_MAX_CONCURRENT_BATCH_RUNS,
            auto_test_max_result_not_started=parsed.AUTO_TEST_MAX_RESULT_NOT_STARTED,
            auto_test_max_unit_test_metadata_length=parsed.AUTO_TEST_MAX_UNIT_TEST_METADATA_LENGTH,
            min_password_score=parsed.MIN_PASSWORD_SCORE,
            reset_token_time=parsed.RESET_TOKEN_TIME,
            setting_token_time=parsed.SETTING_TOKEN_TIME,
            max_number_of_files=parsed.MAX_NUMBER_OF_FILES,
            max_large_upload_size=parsed.MAX_LARGE_UPLOAD_SIZE,
            max_normal_upload_size=parsed.MAX_NORMAL_UPLOAD_SIZE,
            max_dynamo_submission_size=parsed.MAX_DYNAMO_SUBMISSION_SIZE,
            max_file_size=parsed.MAX_FILE_SIZE,
            max_dynamo_file_size=parsed.MAX_DYNAMO_FILE_SIZE,
            max_document_update_size=parsed.MAX_DOCUMENT_UPDATE_SIZE,
            jwt_access_token_expires=parsed.JWT_ACCESS_TOKEN_EXPIRES,
            max_mirror_file_age=parsed.MAX_MIRROR_FILE_AGE,
            max_user_setting_amount=parsed.MAX_USER_SETTING_AMOUNT,
            send_registration_email=parsed.SEND_REGISTRATION_EMAIL,
            auto_test_max_time_command=parsed.AUTO_TEST_MAX_TIME_COMMAND,
            auto_test_io_test_message=parsed.AUTO_TEST_IO_TEST_MESSAGE,
            auto_test_io_test_sub_message=parsed.AUTO_TEST_IO_TEST_SUB_MESSAGE,
            auto_test_run_program_message=parsed.AUTO_TEST_RUN_PROGRAM_MESSAGE,
            auto_test_capture_points_message=parsed.AUTO_TEST_CAPTURE_POINTS_MESSAGE,
            auto_test_checkpoint_message=parsed.AUTO_TEST_CHECKPOINT_MESSAGE,
            auto_test_unit_test_message=parsed.AUTO_TEST_UNIT_TEST_MESSAGE,
            auto_test_code_quality_message=parsed.AUTO_TEST_CODE_QUALITY_MESSAGE,
            exam_login_max_length=parsed.EXAM_LOGIN_MAX_LENGTH,
            login_token_before_time=parsed.LOGIN_TOKEN_BEFORE_TIME,
            site_email=parsed.SITE_EMAIL,
            max_lines=parsed.MAX_LINES,
            notification_poll_time=parsed.NOTIFICATION_POLL_TIME,
            release_message_max_time=parsed.RELEASE_MESSAGE_MAX_TIME,
            max_plagiarism_matches=parsed.MAX_PLAGIARISM_MATCHES,
            auto_test_max_global_setup_time=parsed.AUTO_TEST_MAX_GLOBAL_SETUP_TIME,
            auto_test_max_per_student_setup_time=parsed.AUTO_TEST_MAX_PER_STUDENT_SETUP_TIME,
            assignment_default_grading_scale=parsed.ASSIGNMENT_DEFAULT_GRADING_SCALE,
            blackboard_zip_upload_enabled=parsed.BLACKBOARD_ZIP_UPLOAD_ENABLED,
            rubrics_enabled=parsed.RUBRICS_ENABLED,
            automatic_lti_role_enabled=parsed.AUTOMATIC_LTI_ROLE_ENABLED,
            lti_enabled=parsed.LTI_ENABLED,
            linters_enabled=parsed.LINTERS_ENABLED,
            incremental_rubric_submission_enabled=parsed.INCREMENTAL_RUBRIC_SUBMISSION_ENABLED,
            register_enabled=parsed.REGISTER_ENABLED,
            groups_enabled=parsed.GROUPS_ENABLED,
            auto_test_enabled=parsed.AUTO_TEST_ENABLED,
            course_register_enabled=parsed.COURSE_REGISTER_ENABLED,
            render_html_enabled=parsed.RENDER_HTML_ENABLED,
            email_students_enabled=parsed.EMAIL_STUDENTS_ENABLED,
            peer_feedback_enabled=parsed.PEER_FEEDBACK_ENABLED,
            at_image_caching_enabled=parsed.AT_IMAGE_CACHING_ENABLED,
            student_payment_enabled=parsed.STUDENT_PAYMENT_ENABLED,
            editor_enabled=parsed.EDITOR_ENABLED,
            server_time_correction_enabled=parsed.SERVER_TIME_CORRECTION_ENABLED,
            metric_gathering_enabled=parsed.METRIC_GATHERING_ENABLED,
            grading_notifications_enabled=parsed.GRADING_NOTIFICATIONS_ENABLED,
            feedback_threads_initially_collapsed=parsed.FEEDBACK_THREADS_INITIALLY_COLLAPSED,
            metric_gathering_time_interval=parsed.METRIC_GATHERING_TIME_INTERVAL,
            metric_gathering_event_interval=parsed.METRIC_GATHERING_EVENT_INTERVAL,
            metric_event_buffer_size=parsed.METRIC_EVENT_BUFFER_SIZE,
            metric_evaluation_time_limit=parsed.METRIC_EVALUATION_TIME_LIMIT,
            metric_evaluation_time_chunk_size=parsed.METRIC_EVALUATION_TIME_CHUNK_SIZE,
            metric_gathering_expressions=parsed.METRIC_GATHERING_EXPRESSIONS,
            server_time_diff_tolerance=parsed.SERVER_TIME_DIFF_TOLERANCE,
            server_time_sync_interval=parsed.SERVER_TIME_SYNC_INTERVAL,
        )
        res.raw_data = d
        return res


import os

if os.getenv("CG_GENERATING_DOCS", "False").lower() in ("", "true"):
    # fmt: off
    pass
    # fmt: on
