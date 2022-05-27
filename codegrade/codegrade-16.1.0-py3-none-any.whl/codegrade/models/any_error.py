"""The module that defines the ``AnyError`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from httpx import Response

from ..parsers import ParserFor, make_union
from ..utils import to_dict
from .auto_test_step_validation_exception import (
    AutoTestStepValidationException,
)
from .base_error import BaseError
from .disabled_setting_exception import DisabledSettingException
from .failed_to_send_email_exception import FailedToSendEmailException
from .first_phase_lti_launch_exception import FirstPhaseLTILaunchException
from .group_not_ready_for_submission_exception import (
    GroupNotReadyForSubmissionException,
)
from .ignored_files_exception import IgnoredFilesException
from .invalid_group_exception import InvalidGroupException
from .invalid_io_cases_exception import InvalidIOCasesException
from .invalid_options_exception import InvalidOptionsException
from .missing_cookie_error import MissingCookieError
from .parse_api_exception import ParseAPIException
from .permission_exception import PermissionException
from .upgraded_lti_provider_exception import UpgradedLTIProviderException
from .weak_password_exception import WeakPasswordException

AnyError = t.Union[
    DisabledSettingException,
    WeakPasswordException,
    ParseAPIException,
    InvalidIOCasesException,
    PermissionException,
    FailedToSendEmailException,
    GroupNotReadyForSubmissionException,
    InvalidGroupException,
    AutoTestStepValidationException,
    MissingCookieError,
    IgnoredFilesException,
    InvalidOptionsException,
    UpgradedLTIProviderException,
    FirstPhaseLTILaunchException,
    BaseError,
]
AnyErrorParser = rqa.Lazy(
    lambda: make_union(
        ParserFor.make(DisabledSettingException),
        ParserFor.make(WeakPasswordException),
        ParserFor.make(ParseAPIException),
        ParserFor.make(InvalidIOCasesException),
        ParserFor.make(PermissionException),
        ParserFor.make(FailedToSendEmailException),
        ParserFor.make(GroupNotReadyForSubmissionException),
        ParserFor.make(InvalidGroupException),
        ParserFor.make(AutoTestStepValidationException),
        ParserFor.make(MissingCookieError),
        ParserFor.make(IgnoredFilesException),
        ParserFor.make(InvalidOptionsException),
        ParserFor.make(UpgradedLTIProviderException),
        ParserFor.make(FirstPhaseLTILaunchException),
        ParserFor.make(BaseError),
    ),
)
