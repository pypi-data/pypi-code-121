# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.


class ShapeletsException(Exception):
    """Shapelets base class for exceptions."""


class ShapeletsLoginException(ShapeletsException):
    pass


class ExecutionException(ShapeletsException):
    def __init__(self, network_error: BaseException, content_error: str):
        # pylint: disable=W0231
        self.network_error = network_error
        self.content_error = content_error


class ShapeletsNDArrayException(ShapeletsException):
    pass
