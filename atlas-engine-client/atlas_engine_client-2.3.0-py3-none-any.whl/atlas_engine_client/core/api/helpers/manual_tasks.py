from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, Undefined, config
#from dataclasses_json import CatchAll
from typing import Callable
from urllib import parse

from ..base_client import BaseClient

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ManualTaskQuery:
    limit: int = None
    offset: int = None
    manual_task_instance_id: str = field(metadata=config(field_name="flowNodeInstanceId"), default=None)
    flow_node_id: str = None
    flow_node_name: str = None
    flow_node_lane: str = None
    correlation_id: str = None
    process_definition_id: str = None
    process_model_id: str = None
    process_instance_id: str = None
    state: str = None

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
#@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class ManualTaskResponse:
    manual_task_instance_id: str = field(metadata=config(field_name="flowNodeInstanceId"))
    correlation_id: str
    process_instance_id: str
    process_model_id: str
    #place_holder: CatchAll
    flow_node_name: str = None
    flow_node_id: str = None
    owner_id: str = None
    flow_node_lane: str = None
    process_definition_id: str = None

class ManualTaskHandler(BaseClient):

    BPMN_TYPE = 'bpmn:ManualTask'

    def __init__(self, url: str, identity: Callable=None):
        super(ManualTaskHandler, self).__init__(url, identity)

    def get_manual_tasks(self, query: ManualTaskQuery = ManualTaskQuery(), options: dict={}) -> ManualTaskResponse:

        query_dict = query.to_dict() 
        query_dict.update({
            'state': 'suspended',
            'flowNodeType': ManualTaskHandler.BPMN_TYPE,
        })

        filtered_query = list(filter(lambda dict_entry: dict_entry[1] is not None, query_dict.items()))

        query_str = parse.urlencode(filtered_query, doseq=False)

        path = f"/atlas_engine/api/v1/flow_node_instances?{query_str}"

        response_list_of_dict = self.do_get(path, options)

        if response_list_of_dict.get('totalCount', 0) > 0:
            json_data = response_list_of_dict.get('flowNodeInstances', {})
            response = ManualTaskResponse.schema().load(json_data, many=True)
        else:
            response = []

        return response

    
    def finish_manual_task(self, manual_task_instance_id: str, options: dict={}):
        path = f"/atlas_engine/api/v1/manual_tasks/{manual_task_instance_id}/finish"

        _ = self.do_put(path, {}, options)

        return True
