from typing import Any, Protocol, cast

import jsonpickle
import tblib

from jetpack.config import _symbols


def encode(val: Any) -> bytes:
    encoded = val
    if isinstance(val, BaseException):
        encoded = _pickle_prep_exception(val)
    return bytes(jsonpickle.encode(encoded), "utf-8")


def decode(val: bytes) -> Any:

    _symbols.get_symbol_table().enable_key_overwrite(True)
    decoded = jsonpickle.decode(val)
    _symbols.get_symbol_table().enable_key_overwrite(False)

    if isinstance(decoded, BaseException):
        decoded = _unpickle_prep_exception(decoded)
    return decoded


class ExceptionWithJetpackFields(BaseException):
    jetpack_cause: Any
    jetpack_context: Any
    jetpack_traceback: Any
    __cause__: Any
    __context__: Any
    __traceback__: Any


# pickle_prep_exception prepares the python exception object for json_pickling. It does
# this by converting the native C-object at exception.__traceback__ to be a
# python dict. It does this recursively by following the exception chain via
# exception.__cause__ and exception.__context__.
#
# The "prepared exception" objects are stored at `.jetpack_traceback`,
# `.jetpack_cause` and `jetpack_context` fields.
def _pickle_prep_exception(err: BaseException) -> BaseException:
    error = cast(ExceptionWithJetpackFields, err)

    error.jetpack_traceback = tblib.Traceback(error.__traceback__).to_dict()

    error.jetpack_cause = None
    if error.__cause__ is not None:
        error.jetpack_cause = _pickle_prep_exception(error.__cause__)

    error.jetpack_context = None
    if error.__context__ is not None:
        error.jetpack_context = _pickle_prep_exception(error.__context__)

    return error


# unpickle_prep_exception undoes the changes in pickle_prep_exception, and sets the
# jetpack-specific fields on the exception object to None
def _unpickle_prep_exception(err: BaseException) -> BaseException:
    error = cast(ExceptionWithJetpackFields, err)

    if error.jetpack_traceback is not None:
        error.__traceback__ = tblib.Traceback.from_dict(
            error.jetpack_traceback
        ).as_traceback()

    if error.jetpack_cause is not None:
        error.__cause__ = _unpickle_prep_exception(error.jetpack_cause)

    if error.jetpack_context is not None:
        error.__context__ = _unpickle_prep_exception(error.jetpack_context)

    error.jetpack_cause = None
    error.jetpack_context = None
    error.jetpack_traceback = None

    return error
