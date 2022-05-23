from typing import Any, Dict, List, Optional
from deeplabel.basemodel import DeeplabelBase
from deeplabel.label.labels import DetectionLabel
import deeplabel.client
from logging import getLogger
logger = getLogger(__name__)



class LabelMap(DeeplabelBase):
    """Detection Label"""
    label_id:str
    label:DetectionLabel
    name_lower:Optional[str]
    project_id:str

    @classmethod
    def add_labels_to_project(cls, project_id:str, label_ids:List[str], client:"deeplabel.client.BaseClient")->List["LabelMap"]:
        data = {
            "batch":True,
            "data":[
                {
                    "projectId":project_id,
                    "labelId":label_id
                }
                for label_id in label_ids
            ]
        }
        updated_labelmap = client.post("/labels/projectmaps", data).json()['data']
        for label_map in updated_labelmap:
            label_map['label'] = label_map['labelId']
            label_map['labelId'] = label_map['label']['labelId']
        return [LabelMap(**label_map) for label_map in updated_labelmap]


    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["LabelMap"]:
        resp = client.get("/labels/projectmaps", params=params)
        labels = resp.json()["data"]["labelProjectMaps"]
        return [cls(**label, client=client) for label in labels]
