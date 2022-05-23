from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, Undefined
from dataclasses_json import CatchAll
from typing import Any, Callable, Dict, Optional
from urllib import parse

from ..base_client import BaseClient

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataObjectInstancesQuery:
    limit: int = None
    offset: int = None
    data_object_id: str = None
    process_definition_id: str = None
    process_model_id: str = None
    process_instance_id: str = None
    flow_node_instance_id: str = None

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class DataObjectInstanceResponse:
    data_object_id: Optional[str] = None
    flow_node_instance_id: Optional[str] = None
    process_definition_id: Optional[str] = None
    process_model_id: Optional[str] = None
    process_instance_id: Optional[str] = None
    value: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    place_holder: CatchAll = None
    
class DataObjectInstanceHandler(BaseClient):

    def __init__(self, url: str, identity: Callable=None):
        super(DataObjectInstanceHandler, self).__init__(url, identity)

    def get_data_object_instances(self, query: DataObjectInstancesQuery, options: dict={}) -> DataObjectInstanceResponse:

        query_dict = query.to_dict() 

        filtered_query = list(filter(lambda dict_entry: dict_entry[1] is not None, query_dict.items()))

        query_str = parse.urlencode(filtered_query, doseq=False)

        path = f"/atlas_engine/api/v1/data_object_instances/query?{query_str}"

        response_list_of_dict = self.do_get(path, options)

        if response_list_of_dict.get('totalCount', 0) > 0:
            json_data = response_list_of_dict['dataObjectInstances']
            response = DataObjectInstanceResponse.schema().load(json_data, many=True)
        else:
            response = []

        return response
