class ConfigurationError(RuntimeError):
    """ General Error. """


class MissingEndpointError(ConfigurationError):
    """ Raised when a request endpoint is not registered. """


class UnknownClientShortTypeError(ConfigurationError):
    """ Raised when a given short service type is not recognized """
