import json
import base64
from os import path
from typing import Any, Tuple

from bloc_client.value_type import ValueType
from bloc_client.internal.http_util import syn_get_to_server, sync_post_to_server


ObjectStorageDataByKeyFromServerPath = "get_byte_value_by_key"
PersistOptDataToServerPath = "persist_certain_function_run_opt_field"

def get_data_by_object_storage_key(
    server_url: str, 
    object_storage_key: str, 
    value_type: ValueType,
    is_array: bool
) -> Tuple[Any, Exception]:
    resp, err = syn_get_to_server(
        server_url + path.join(
            ObjectStorageDataByKeyFromServerPath, 
            object_storage_key),
        {})
    if err:
        return None, err
    try:
        data_in_str = base64.b64decode(resp).decode()
        if is_array:
            data_list = eval(data_in_str)
            return data_list, None
        else:
            if value_type == ValueType.strValueType:
                if data_in_str.startswith('"'):
                    data_in_str = data_in_str[1:]
                if data_in_str.endswith('"'):
                    data_in_str = data_in_str[:len(data_in_str)-1]
                return data_in_str, None
            elif value_type == ValueType.intValueType:
                return int(data_in_str), None
            elif value_type == ValueType.floatValueType:
                return float(data_in_str), None
            elif value_type == ValueType.jsonValueType:
                return json.loads(data_in_str)
            elif value_type == ValueType.boolValueType:
                return False if data_in_str in ["0", "false", "False"] else True
    except Exception as e:
        return None, e

def persist_opt_to_server(
    trace_id: str, 
    span_id: str,
    server_url: str, 
    function_run_record_id: str, 
    opt_key: str, opt_data: Any
) -> Tuple[Any, Exception]:
    data = {
        'function_run_record_id': function_run_record_id,
        'opt_key': opt_key,
        'data': opt_data}
    resp, err = sync_post_to_server(
        server_url + path.join(PersistOptDataToServerPath),
        data, 
        headers={
            "trace_id": trace_id,
            "span_id": span_id
        }
    )
    if err:
        return None, err
    try:
        return resp, None
    except Exception as e:
        return None, e
