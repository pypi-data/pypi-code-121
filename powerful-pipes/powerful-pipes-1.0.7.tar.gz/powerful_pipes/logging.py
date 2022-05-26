import sys
import time
import traceback

from .typing import JSON
from .io_utils import write_json_to_stderr
from .async_io_utils import async_write_json_to_stderr


class REPORT_LEVEL:
    EXCEPTION = 50
    CRITICAL = 40
    ERROR = 30
    WARNING = 20
    INFO = 10
    DEBUG = 0


def _make_report_(
        original_data: JSON,
        log_level: int = REPORT_LEVEL.INFO,
        data: dict = None,
        message: str = None
) -> dict:

    binary_report = {
        "logLevel": log_level,
        "commandLine": " ".join(sys.argv),
        "epoch": time.time(),
    }

    exc_type, exc_obj, exc_tb = sys.exc_info()

    if exc_type:
        exc = {
            "exceptionName": exc_type.__name__,
            "exceptionMessage": str(exc_obj),
            "binary": exc_tb.tb_frame.f_code.co_filename,
            "stackTrace": "\n".join(traceback.format_tb(exc_tb))
        }

        if data:
            if user_exc := data.get("exception", None):
                exc["userException"] = str(user_exc)

        binary_report["exceptionDetails"] = exc

    if message:
        binary_report["message"] = message

    if data:
        binary_report["data"] = data

    report = {
        sys.argv[0]: binary_report
    }

    if not original_data:
        original_data = {"_meta": {"reporting": report}}

    else:
        original_data.setdefault("_meta", {}).setdefault("reporting", report)

    return original_data


def report(
        original_data: JSON = None,
        log_level: int = REPORT_LEVEL.INFO,
        data: JSON = None,
        message: str = None
):
    write_json_to_stderr(_make_report_(
        original_data,
        log_level,
        data,
        message
    ))

def eprint(message: str):
    report(message=message, log_level=REPORT_LEVEL.INFO)


def report_exception(
        original_data: JSON,
        exception: Exception,
        message: str = None
):
    write_json_to_stderr(_make_report_(
        original_data,
        log_level=REPORT_LEVEL.EXCEPTION,
        data={
            "exception": str(exception)
        },
        message=message
    ))


async def async_report_exception(
        original_data: JSON or None,
        exception: Exception,
        message: str = None
):
    await async_write_json_to_stderr(_make_report_(
        original_data,
        log_level=REPORT_LEVEL.EXCEPTION,
        data={
            "exceptionDetails": str(exception)
        },
        message=message
    ))


__all__ = (
    "report", "REPORT_LEVEL", "report_exception", "async_report_exception",
    "eprint"
)
