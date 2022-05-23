import os
import functools
from logging import getLogger, FileHandler, Formatter
import coloredlogs
import tempfile
from importlib.metadata import version
logger = getLogger(__name__)

# Create an error logger specifically for logging unexpected errors to /tmp/deeplabel-sdk-errors.logs
error_logger = getLogger('Error')
error_logger.propagate = False
log_file = os.path.join(tempfile.gettempdir(), 'deeplabel-sdk-errors.logs') 
error_file_handler=FileHandler(log_file)
error_file_handler.setFormatter(Formatter('%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'))
error_logger.addHandler(error_file_handler)
error_logger.error(f"deeplabel-sdk version: {version('deeplabel-sdk')}")

# Root Exception Class for all Deeplabel related Exceptions
class DeeplabelException(Exception):...


class InvalidCredentials(DeeplabelException):...


# Error representing invalid Id for any or detectionId,VideoId,GraphId,NodeId,EdgeId,etc
class InvalidIdError(DeeplabelException):...


# If an api returns response_code > 200
class InvalidAPIResponse(DeeplabelException):...

# VideoUrl doesn't exist anymore
class DownloadFailed(DeeplabelException):...


# Raise when you need to raise value error but handle gracefully since it's client facing
class DeeplabelValueError(DeeplabelException):...


def handle_deeplabel_exceptions(default_factory):
    """Run the func and catch DeeplabelExceptions, and return a default output
    Decorate functions that run in multiprocessing, to process videos/galleries/etc
    in parallel, so that they can be gracefully handled to return some default value
    """
    def caller(func):
        @functools.wraps(func)
        def inner(*args,**kwargs):
            try:
                return func(*args, **kwargs)
            except DeeplabelException as e:
                logger.error(e)
                logger.debug(e, exc_info=True)
                return default_factory()
            except Exception as e:
                logger.error(f"Unexpected error occured: {e}. Please report with the log file {log_file}")
                error_logger.error(f"{'-'*80}\n{'-'*80}\n{e}\n\nargs:{args}\n\nkwargs: {kwargs}", exc_info=True)
                return default_factory()
        return inner
    return caller