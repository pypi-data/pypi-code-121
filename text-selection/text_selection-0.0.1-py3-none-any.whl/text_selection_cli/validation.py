
from enum import IntEnum

from text_selection_core.validation import ValidationErrBase


class CliErrorType(IntEnum):
  FILE_NOT_READABLE = 0
  FILE_NOT_WRITEABLE = 1


_DEFAULT_ERROR_PATTERNS = {
  CliErrorType.FILE_NOT_READABLE:
    "{0} \"{1}\" couldn't be read!",
  CliErrorType.FILE_NOT_WRITEABLE:
    "{0} \"{1}\" couldn't be written!",
}


class CliValidationErr(ValidationErrBase):
  def __init__(self, error_type: CliErrorType, *msg_args: object) -> None:
    super().__init__()
    self.__error_type = error_type
    self.__args = msg_args

  @property
  def default_message(self) -> str:
    result = str.format(_DEFAULT_ERROR_PATTERNS[self.__error_type], *self.__args)
    return result

  @property
  def error_type(self) -> CliErrorType:
    return self.__error_type

  @property
  def msg_args(self) -> object:
    return self.__args
