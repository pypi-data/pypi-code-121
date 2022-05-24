"""
Exceptions
^^^^^^^^^^

Exceptions used by the quality module.
"""

################################
# Exceptions
################################


class NotInitialized(Exception):
    """Initialize to discover all available expectation
    implementations. It has not happened.
    """

    pass


class InvalidExpectation(Exception):
    """
    Invalid specification of expectations
    """

    pass


class NoExpectations(Exception):
    """
    Empty list of expectations to evaluate
    """

    pass


class UnsupportedExpectation(Exception):
    """
    Expectation name or content not implemented/supported.
    """

    pass


class IncorrectImplementationExpectation(Exception):
    """
    Expectation implementation class didnt return right result
    """

    pass


class InvalidConfigurationExpectation(Exception):
    """
    Expectation implementation class didnt return right result
    """

    pass
