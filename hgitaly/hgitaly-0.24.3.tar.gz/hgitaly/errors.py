# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import StatusCode
import logging

logger = logging.getLogger(__name__)

HGITALY_ISSUES_URL = "https://foss.heptapod.net/heptapod/hgitaly/-/issues"


class ServiceError(RuntimeError):
    """An exception class to complement setting of context.

    In case when it is not practical for service methods to early return
    using functions such as :func:`not_found`, this exception can be used
    as marker that a problem was encountered *and handled by updating
    gRPC context*.
    """


def not_implemented(context, response_cls, issue: int):
    """Return grpc proper UNIMPLENTED code with tracking issue URL details.

    One minor goal is that the caller can use this with a single statement::

       return not_implemented(context, MyResponse, issue=3)  # pragma no cover

    with the benefit to need only one "no cover" directive.

    Note: returning a proper Response message is mandatory in all cases,
    to avoid this::

      [2020-11-09 12:33:03 +0100] [793335] [ERROR] [grpc._common] Exception serializing message!
      Traceback (most recent call last):
      File "/home/gracinet/heptapod/hdk/default/venv3/lib/python3.8/site-packages/grpc/_common.py", line 86, in _transform
        return transformer(message)
      TypeError: descriptor 'SerializeToString' for 'google.protobuf.pyext._message.CMessage' objects doesn't apply to a 'NoneType' object
    """  # noqa
    context.set_code(StatusCode.UNIMPLEMENTED)
    msg = "Not implemented. Tracking issue: %s/%d" % (HGITALY_ISSUES_URL,
                                                      issue)
    logger.error(msg)
    context.set_details(msg)
    return response_cls()


def not_found(context, response_cls, message, log_level=logging.WARNING):
    """Return grpc proper NOT_FOUND code with message.

    This helper method saves at most 3 lines of code, and that makes a
    difference for repetitive error treatment. It's also good for
    uniformity.

    The default value for `log_level` is based on the assumption that
    the client should have the means to perform calls that don't end up
    in gRPC errors, be it by before hand knowledge or by using calls that
    have a specified return for missing content. Still, ``log_level`` is
    provided for cases where the server would know that warnings are too much.
    """
    context.set_code(StatusCode.NOT_FOUND)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def internal_error(context, response_cls, message, log_level=logging.ERROR):
    """Return grpc INTERNAL code with message.

    Similar to :func:`not_found`, except for the default ``log_level``
    """
    context.set_code(StatusCode.INTERNAL)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def invalid_argument(context, response_cls, message, log_level=logging.ERROR):
    """Return grpc INVALID_ARGUMENT code with message.

    Similar to :func:`not_found`, except for the default ``log_level``
    """
    context.set_code(StatusCode.INVALID_ARGUMENT)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def unknown_error(context, response_cls, message, log_level=logging.ERROR):
    """Return grpc UNKNOWN code with message.

    Similar to :func:`not_found`, except for the default ``log_level``
    """
    context.set_code(StatusCode.UNKNOWN)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def already_exists(context, response_cls, message, log_level=logging.WARN):
    """Return grpc UNKNOWN code with message.

    Similar to :func:`not_found`, except for the default ``log_level``
    """
    context.set_code(StatusCode.ALREADY_EXISTS)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def unavailable_error(context, response_cls, message, log_level=logging.ERROR):
    """Return grpc UNAVAILABLE code with message.

    Similar to :func:`not_found`, except for the default ``log_level``
    """
    context.set_code(StatusCode.UNAVAILABLE)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def failed_precondition(context, response_cls, message,
                        log_level=logging.INFO):
    """Return grpc FAILED_PRECONDITION code with message.

    Similar to :func:`not_found`, except for the default ``log_level``,
    which is ``INFO`` because it seems to be used for routine stuff, like
    fetching data only if size is smaller than a given limit.
    """
    context.set_code(StatusCode.FAILED_PRECONDITION)
    logger.log(log_level, message)
    context.set_details(message)
    return response_cls()


def no_response():
    """Placeholder to use the above error functions without a response class.

    To use in conjunction with :class:`ServiceError` exceptions.
    This is a transitional compatibility layer, less confusing than using
    an actual Response class when we don't care about response yet in error
    treatment.

    :returns: ``None``
    """
