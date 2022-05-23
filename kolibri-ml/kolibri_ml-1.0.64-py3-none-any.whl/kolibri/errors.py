from typing import Text
from kolibri.logger import get_logger

logger=get_logger(__name__)

class MissingArgumentError(ValueError):
    """Raised when a function is called and not all parameters can be
    filled from the context / config.

    Attributes:
        document -- explanation of which parameter is missing
    """

    def __init__(self, document, message):
        self.document = document
        logger.error(message)

    def __str__(self):
        return self.document


class UnsupportedLanguageError(Exception):
    """Raised when a component is created but the language is not supported.

    Attributes:
        component -- component name
        language -- language that component doesn't support
    """

    def __init__(self, component, language, message):
        self.component = component
        self.language = language

        logger.error(message)


    def __str__(self):
        return "component {} does not support language {}".format(
            self.component, self.language
        )


class InvalidConfigError(ValueError):
    """Raised if an invalid configuration is encountered."""

    def __init__(self, message):
        super(InvalidConfigError, self).__init__(message)

        logger.error(message)


class InvalidProjectError(Exception):
    """Raised when a model_type failed to load.

    Attributes:
        document -- explanation of why the model_type is invalid
    """

    def __init__(self, message, document=None):
        self.document = document
        logger.error(message)

    def __str__(self):
        return self.document


class UnsupportedModelError(Exception):
    """Raised when a model_type is too old to be loaded.

    Attributes:
        document -- explanation of why the model_type is invalid
    """

    def __init__(self, document, message):
        self.document = document
        logger.error(message)
    def __str__(self):
        return self.document

class AxisLabelsMismatchError(ValueError):
    """Raised when a pair of axis labels tuples do not match."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class ConfigurationError(Exception):
    """Error raised when a configuration value is requested but not set."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class MissingInputFiles(Exception):
    """Exception raised by a converter when input files are not found.

    Parameters
    ----------
    message : str
        The error message to be associated with this exception.
    filenames : list
        A list of filenames that were not found.

    """
    def __init__(self, message, filenames):
        self.filenames = filenames
        super(MissingInputFiles, self).__init__(message, filenames)
        logger.error(message)

class NeedURLPrefix(Exception):
    """Raised when a URL is not provided for a file."""
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)

class MetricException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        logger.error(message)