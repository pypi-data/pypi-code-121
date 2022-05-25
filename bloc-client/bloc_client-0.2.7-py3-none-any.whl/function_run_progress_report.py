from os import path
from typing import Optional
from dataclasses import dataclass

from bloc_client.internal.http_util import sync_post_to_server

FuncRunProgressReportPath = "report_progress"


@dataclass
class HighReadableFunctionRunProgress:
    progress_percent: Optional[float]=None
    msg: Optional[str]=None
    progress_milestone_index: Optional[int]=None

    @property
    def to_server_dict(self):
        resp = {}
        if not any([self.progress_milestone_index, self.progress_percent, self.msg]):
            return resp
        if self.progress_percent:
            resp['progress'] = self.progress_percent
        if self.progress_milestone_index is not None and isinstance(self.progress_milestone_index, int):
            resp['progress_milestone_index'] = self.progress_milestone_index
        if self.msg:
            resp['msg'] = self.msg
        return resp

def report_function_run_high_readable_progress(
    trace_id: str, 
    span_id: str,
    server_url: str,
    function_run_record_id: str, 
    function_run_progress: HighReadableFunctionRunProgress,
) -> Exception:
    if not all([function_run_progress.to_server_dict, function_run_record_id]):
        return None

    data = {
        "function_run_record_id": function_run_record_id,
        "high_readable_run_progress": function_run_progress.to_server_dict
    }
    resp, err = sync_post_to_server(
        server_url + path.join(FuncRunProgressReportPath),
        data, headers= {
            "trace_id": trace_id,
            "span_id": span_id
        }
    )
    return err
