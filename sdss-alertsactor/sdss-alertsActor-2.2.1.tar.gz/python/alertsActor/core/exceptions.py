# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class AlertsactorError(Exception):
    """A custom core Alertsactor exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(AlertsactorError, self).__init__(message)


class AlertsactorNotImplemented(AlertsactorError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(AlertsactorNotImplemented, self).__init__(message)


class AlertsactorApiError(AlertsactorError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Alertsactor API'
        else:
            message = 'Http response error from Alertsactor API. {0}'.format(message)

        super(AlertsactorAPIError, self).__init__(message)


class AlertsactorApiAuthError(AlertsactorAPIError):
    """A custom exception for API authentication errors"""
    pass


class AlertsactorMissingDependency(AlertsactorError):
    """A custom exception for missing dependencies."""
    pass


class AlertsactorWarning(Warning):
    """Base warning for Alertsactor."""
    pass


class AlertsactorUserWarning(UserWarning, AlertsactorWarning):
    """The primary warning class."""
    pass


class AlertsactorSkippedTestWarning(AlertsactorUserWarning):
    """A warning for when a test is skipped."""
    pass


class AlertsactorDeprecationWarning(AlertsactorUserWarning):
    """A warning for deprecated features."""
    pass

