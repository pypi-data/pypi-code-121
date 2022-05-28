"""A collection of custom errors used in Chart Me

helpful url found here:
https://www.programiz.com/python-programming/user-defined-exception
reminder: default behavior accepts a message
"""


class ColumnDoesNotExistsError(Exception):
    """Implementation to track if column not found in pandas"""

    pass


class ColumnAllNullError(Exception):
    """Implementation of error if column is all nulls"""

    pass


class ColumnTooManyNullsError(Exception):
    """Implementation of error if columns has too many nulls"""

    def __init__(self, null_rate, message="Null Rate below Threshold"):
        """set variables"""
        self.null_rate = null_rate
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Override string representations"""
        return f"{self.null_rate} calculated --> {self.message}"


class InsufficientValidColumnsError(Exception):
    """Implementation of error if there's no valid columns to chart"""

    pass
