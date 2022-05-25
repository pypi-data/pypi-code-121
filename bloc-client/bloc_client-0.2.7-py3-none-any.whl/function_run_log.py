from os import path
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from bloc_client.internal.http_util import sync_post_to_server

LogReportPath = "report_log"


class LogLevel(Enum):
    info = "info"
    warning = "warning"
    error = "error"
    unknown = "unknown"


@dataclass
class FunctionRunMsg:
    level: LogLevel
    msg: str


@dataclass
class LogMsg:
    level: LogLevel
    data: str
    function_run_record_id: str
    time: datetime=field(default_factory=datetime.utcnow)

    def json_dict(self):
        return {
            "level": self.level.value,
            "data": self.data,
            "time": self.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "tag_map": {
                "function_run_record_id": self.function_run_record_id
            }
        }


@dataclass
class Logger:
    _server_url: str
    function_run_record_id: str
    trace_id: str=""
    span_id: str=""

    @staticmethod
    def New(server_url:str, function_run_record_id:str) -> "Logger":
        return Logger(
            _server_url=server_url,
            function_run_record_id=function_run_record_id)
    
    def set_trace_id(self, trace_id: str):
        self.trace_id = trace_id
    
    def set_span_id(self, span_id: str):
        self.span_id = span_id
    
    def info(self, msg: str):
        self.upload(LogLevel.info, msg)

    def warning(self, msg: str):
        self.upload(LogLevel.warning, msg)
    
    def error(self, msg: str):
        self.upload(LogLevel.error, msg)
    
    def unknown(self, msg: str):
        self.upload(LogLevel.unknown, msg)
    
    def add_msg(self, func_run_msg: FunctionRunMsg):
        if func_run_msg.level == LogLevel.info:
            self.info(func_run_msg.msg)
        elif func_run_msg.level == LogLevel.warning:
            self.warning(func_run_msg.msg)
        elif func_run_msg.level == LogLevel.error:
            self.error(func_run_msg.msg)
        else:
            self.unknown(func_run_msg.msg)

    def upload(self, level: LogLevel, data: str):
        msg = LogMsg(
            level=level,
            data=data,
            function_run_record_id=self.function_run_record_id)

        _, err = sync_post_to_server(
            path.join(self._server_url, LogReportPath),
            data={"logs": [msg.json_dict()]},
            headers={
                "trace_id": self.trace_id,
                "span_id": self.span_id}
        )
        return err
