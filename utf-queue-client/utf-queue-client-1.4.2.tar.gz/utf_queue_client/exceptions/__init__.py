from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError

__all__ = ["SchemaValidationError", "ValidationError", "ValidationErrorBase"]


class ValidationErrorBase(Exception):
    """ Base class for validation error """


class SchemaValidationError(ValidationErrorBase):
    def __init__(self, validation_error: JsonSchemaValidationError):
        super().__init__(validation_error.message)
        self.validation_error = validation_error


class ValidationError(ValidationErrorBase):
    def __init__(self, validation_error: PydanticValidationError):
        super().__init__(str(validation_error))
        self.validation_error = validation_error
