from datetime import datetime
from pythonjsonlogger.jsonlogger import JsonFormatter


class CustomJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.now().isoformat()
        log_record["logger"] = record.name
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("stack", "backend")
