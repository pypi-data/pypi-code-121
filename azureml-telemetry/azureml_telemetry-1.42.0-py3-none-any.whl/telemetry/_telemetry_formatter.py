# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""PII-aware logging formatter."""
import logging


class ExceptionFormatter(logging.Formatter):
    """Formatter for exceptions being sent to Application Insights."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Modify the log record to strip error messages if they originate from a non-AzureML exception, then format.

        :param record: Logging record.
        :return: Formatted record.
        """
        exception_tb = getattr(record, "exception_tb_obj", None)
        if exception_tb is None:
            return super().format(record)

        not_available_message = "[Not available]"

        properties = getattr(record, "properties", {})

        message = properties.get("exception_message", "[Hidden as it may contain PII]")
        traceback_msg = properties.get("exception_traceback", not_available_message)

        record.message = record.msg = "\n".join(
            [
                "Type: {}".format(properties.get("error_type", "Unclassified")),
                "Class: {}".format(properties.get("exception_class", not_available_message)),
                "Message: {}".format(message),
                "Traceback: {}".format(traceback_msg),
                "ExceptionTarget: {}".format(properties.get("exception_target", not_available_message)),
            ]
        )

        # Update exception message and traceback in extra properties as well
        properties["exception_message"] = message

        return super().format(record)
