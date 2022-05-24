"""eox-audit-model context_managers file.

Functions:
    capture_logs: Allow to get a logs copy.
"""
import logging
from contextlib import contextmanager

from django.conf import settings

from eox_audit_model.constants import LOG_FORMAT

LOG = logging.getLogger()


@contextmanager
def capture_logs():
    """Capture the execution logs in a inner class.

    Return:
        yield: Instance of CaptureLogsHandler.
    """

    class CaptureLogsHandler(logging.StreamHandler):
        """CaptureLogsHandler class.

        Allow to override the emit method and store the records in a class field.

        Attributes:
            formatted_records: Logs list.
        """

        formatted_records = []

        def emit(self, record):
            """Override standard behavior, in order to store the records with an specific format.

            Arguments:
                record: Log record.
            """
            self.formatted_records.append(self.format(record))

    formaters = settings.LOGGING.get('formatters', {})
    standard_format = formaters.get('standard', {})
    log_format = standard_format.get('format', LOG_FORMAT)
    capture_logs_handler = CaptureLogsHandler()
    capture_logs_handler.setFormatter(logging.Formatter(log_format))
    LOG.addHandler(capture_logs_handler)

    try:
        yield capture_logs_handler
    finally:
        capture_logs_handler.close()
        LOG.removeHandler(capture_logs_handler)
