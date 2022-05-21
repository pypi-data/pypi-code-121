"""
AIML exceptions raised during the evaluation of the response.

For the errors encountered during data parsing, refer to
`parser` module.
"""


class AIMLError(Exception):
    """Generic exception raised during AIML evaluation."""


class NoMatchingCategory(AIMLError):
    """When no match is found in the graphmaster."""
