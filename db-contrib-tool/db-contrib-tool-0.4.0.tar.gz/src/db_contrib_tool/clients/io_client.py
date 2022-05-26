"""Client for working with input/output."""
import sys


class IOClient:
    """Client for working with input/output."""

    @staticmethod
    def read_from_stdin() -> str:
        """
        Read from standard input.

        :return: Standard input string.
        """
        return sys.stdin.read()
