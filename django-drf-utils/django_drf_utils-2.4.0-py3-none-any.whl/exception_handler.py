import logging

from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler
from .exceptions import UnprocessableEntityError

logger = logging.getLogger(__name__)


def exception_logger(exception: Exception, _):
    """Logs given exception (because it is not done by default handler)."""
    if exception and isinstance(
        exception, (NotAuthenticated, UnprocessableEntityError)
    ):
        # user is not logged in
        # or entered wrong data which has been detected
        logger.info(exception)
    else:
        logger.error(exception)
    return exception_handler(exception, _)
