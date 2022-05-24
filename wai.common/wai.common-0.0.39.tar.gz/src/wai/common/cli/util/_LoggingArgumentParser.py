from argparse import ArgumentParser
from sys import stderr
from typing import Optional, IO

from ...logging import LoggingMixin


class LoggingArgumentParser(ArgumentParser, LoggingMixin):
    """
    An argument parser that logs messages instead of printing
    them to stdout/stderr.
    """
    def _print_message(self, message: str, file: Optional[IO[str]] = None):
        if message:
            # Copy the base argument parser's default for file
            if file is None:
                file = stderr

            # Choose a logger based on the output stream
            if file is stderr:
                logger = self.logger.error
            else:
                logger = self.logger.warning

            # Log the message
            logger(message)
