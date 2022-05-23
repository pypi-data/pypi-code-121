# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class UserErrorException(Exception):
    """Exception raised when invalid or unsupported inputs are provided."""

    def __init__(self, message):
        super().__init__(message)


class ComponentDefiningError(UserErrorException):
    """This error indicates that the user define a mldesigner.command_component in an incorrect way."""

    def __init__(self, cause):
        """Init the error with the cause which causes the wrong mldesigner.command_component."""
        msg = "Defining the component failed due to {}."
        super().__init__(message=msg.format(cause))


class NoComponentError(UserErrorException):
    """Exception when no valid mldesigner component found in specific file."""

    def __init__(self, file, name=None):
        """Error message inits here."""
        if name:
            msg = "No mldesigner.command_component with name {} found in {}."
            super().__init__(message=msg.format(name, file))
        else:
            msg = "No mldesigner.command_component found in {}."
            super().__init__(message=msg.format(file))


class RequiredComponentNameError(UserErrorException):
    """Exception when multiple mldesigner.command_components are found and no component name specified."""

    def __init__(self, file):
        """Error message inits here."""
        msg = "More than one mldesigner.command_component found in {}, '--name' parameter is required."
        super().__init__(message=msg.format(file))


class TooManyComponentsError(UserErrorException):
    """Exception when multiple mldesigner.command_components are found in single component entry."""

    def __init__(self, count, file, component_name=None):
        """Error message inits here."""
        if not component_name:
            msg = "Only one mldesigner.command_component is allowed per file, {} found in {}".format(count, file)
        else:
            msg = "More than one mldesigner.command_component with name %r found in %r, count %d." % (
                component_name,
                file,
                count,
            )
        super().__init__(message=msg)


class RequiredParamParsingError(UserErrorException):
    """This error indicates that a parameter is required but not exists in the command line."""

    def __init__(self, name, arg_string):
        """Init the error with the parameter name and its arg string."""
        msg = "'{}' cannot be None since it is not optional. Please make sure command option '{}' exists."
        super().__init__(message=msg.format(name, arg_string))


class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ImportException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ComponentException(Exception):
    def __init__(self, message):
        super().__init__(message)
