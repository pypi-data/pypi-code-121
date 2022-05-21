from os import path
from datetime import datetime
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from bloc_client.function_run_opt import FunctionRunOpt
from bloc_client.internal.http_util import syn_get_to_server, sync_post_to_server

FunctionRunRecordPath = "get_function_run_record_by_id"
FunctionRunStartPath = "function_run_start"
FunctionRunFinishedPath = "function_run_finished"
ClientAliveHeartBeat = "report_functionExecute_heartbeat"


@dataclass
class BriefAndKey:
    brief: str
    object_storage_key: str


@dataclass
class FunctionRunRecord:
    id: str
    flow_id: str
    function_id: str
    flow_run_record_id: str
    canceled: str
    trace_id: str=""
    ipt: List[List[BriefAndKey]] = field(default_factory=list)
    should_be_canceled_at: Optional[datetime]=None

def get_functionRunRecord_by_id(
    server_url: str,
    func_run_record_id: str
) -> Tuple[FunctionRunRecord, Exception]:
    resp, err = syn_get_to_server(
        server_url + path.join(FunctionRunRecordPath, func_run_record_id),
        {})
    if err:
        return None, err

    try:
        ipts = []
        function_run_record = FunctionRunRecord(
            id=resp['id'],
            flow_id=resp['flow_id'],
            function_id=resp['function_id'],
            flow_run_record_id=resp['flow_function_id'],
            canceled=resp.get('canceled', False),
            trace_id=resp['trace_id'],
            ipt=ipts
        )
        # TODO 处理should_be_canceled_at字段
        for ipt in resp['ipt']:
            tmp = []
            for component in ipt:
                tmp.append(
                    BriefAndKey(
                        brief=component['brief'],
                        object_storage_key=component['object_storage_key']
                    )
                )
            ipts.append(tmp)

        return function_run_record, None
    except Exception as e:
        return None, e

def report_function_run_start(
    trace_id: str, 
    span_id: str,
    server_url: str,
    function_run_record_id: str, 
) -> Exception:
    _, err = sync_post_to_server(
        server_url + path.join(FunctionRunStartPath),
        {"function_run_record_id": function_run_record_id},
        headers={
            "trace_id": trace_id,
            "span_id": span_id
        }
    )
    return err

def report_function_run_finished(
    trace_id: str, 
    span_id: str,
    server_url: str,
    function_run_record_id: str, 
    function_run_opt: FunctionRunOpt,
) -> Exception:
    data = function_run_opt.finished_report_dict
    data['function_run_record_id'] = function_run_record_id
    resp, err = sync_post_to_server(
        server_url + path.join(FunctionRunFinishedPath),
        data,
        headers={
            "trace_id": trace_id,
            "span_id": span_id
        }
    )
    return err

def report_function_run_heartbeat(
    trace_id: str, 
    span_id: str,
    server_url: str,
    function_run_record_id: str, 
) -> Exception:
    resp, err = syn_get_to_server(
        server_url + path.join(ClientAliveHeartBeat, function_run_record_id),
        params={},
        headers={
            "trace_id": trace_id,
            "span_id": span_id
        }
    )
    return err
