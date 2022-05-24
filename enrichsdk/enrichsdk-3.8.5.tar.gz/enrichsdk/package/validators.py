import os
from prompt_toolkit.validation import Validator, ValidationError

#################################################
# Validators
#################################################
class NameValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Input should not be empty", cursor_position=len(document.text)
            )  # Move cursor to end of input.


class RealtimeBatchValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Computation should not be empty",
                cursor_position=len(document.text),
            )
        if document.text not in ["batch", "realtime"]:
            raise ValidationError(
                message="Valid values are 'batch' and 'realtime'",
                cursor_position=len(document.text),
            )


class EmailValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Email should not be empty", cursor_position=len(document.text)
            )
        if "@" not in document.text:
            raise ValidationError(
                message="Invalid email address", cursor_position=len(document.text)
            )


class OrgDescValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Customer organization description should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class GenericDescValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Customer organization description should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class LogoValidator(Validator):
    def validate(self, document):
        url = document.text
        if len(url) == 0:
            raise ValidationError(
                message="Customer logo URL should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.
        if not url.startswith("http"):
            raise ValidationError(
                message="Customer logo URL should be a valid URL (http://...",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.
        if not (
            url.lower().endswith("png")
            or url.lower().endswith("gif")
            or url.lower().endswith("jpg")
            or url.lower().endswith("ico")
        ):
            raise ValidationError(
                message="Customer logo URL should be a valid URL (http://....png",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class URLValidator(Validator):
    def validate(self, document):
        url = document.text
        if len(url) == 0:
            raise ValidationError(
                message="URL should not be empty", cursor_position=len(document.text)
            )  # Move cursor to end of input.
        if not url.startswith("http"):
            raise ValidationError(
                message="URL should be a valid URL (http://...",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class ValidDir(Validator):
    def validate(self, document):
        if (
            (len(document.text) == 0)
            or (not os.path.exists(document.text))
            or (not os.path.isdir(document.text))
        ):
            raise ValidationError(
                message="Directory specified doesnt exist or is invalid",
                cursor_position=len(document.text),
            )


class ValidFile(Validator):
    def validate(self, document):
        if (
            (len(document.text) == 0)
            or (not os.path.exists(document.text))
            or (not os.path.isfile(document.text))
        ):
            raise ValidationError(
                message="File specified doesnt exist or is invalid",
                cursor_position=len(document.text),
            )
