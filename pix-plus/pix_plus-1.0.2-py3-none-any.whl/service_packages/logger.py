from pythonjsonlogger import jsonlogger
from datetime import datetime
import logging
from _version import __version__

logger = logging.getLogger("Facial-Process")

logHandler = logging.StreamHandler()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("datetime"):
            log_record["time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        log_record["version"] = str(__version__)


formatter = CustomJsonFormatter("%(time)s %(level)s %(message)s")

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)
