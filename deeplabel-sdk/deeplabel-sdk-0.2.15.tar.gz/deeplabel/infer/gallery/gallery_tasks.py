"""
Module to get videotasks data
"""
from enum import Enum
from itertools import islice
from typing import Any, Iterable, List, Dict, Optional
import deeplabel.infer.graphs.graph_nodes
import deeplabel.infer.gallery.detections as gallery_detections
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from pydantic import conint, Field, validate_arguments
from logging import getLogger
import json

logger = getLogger(__name__)

class GalleryTaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    ABORTED = "ABORTED"
    FAILURE = "FAILURE"
    NOT_AVAILABLE = "NOT_AVAILABLE"

class GraphNodeAnnotation(MixinConfig):
    name:str
    graph_node_id:str

class GalleryAnnotation(MixinConfig):
    title:str
    gallery_id:str

class GalleryTask(DeeplabelBase):
    gallery_task_id: str
    gallery:GalleryAnnotation = Field(...,alias='galleryId')
    graph_id: str
    project_id:str
    graph_node: GraphNodeAnnotation = Field(..., alias='graphNodeId')
    is_shown: bool
    name: str
    status: GalleryTaskStatus
    progress: int

    @classmethod
    def _from_search_params(cls, params: Dict[str, str], client: "deeplabel.client.BaseClient") -> List["GalleryTask"]:  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/gallery/tasks", params=params)
        tasks = resp.json()["data"]["galleryTasks"]
        # Checkout https://lidatong.github.io/dataclasses-json/#use-my-dataclass-with-json-arrays-or-objects
        tasks = [cls(**task, client=client) for task in tasks]
        return tasks #type: ignore

    @classmethod
    def from_gallery_task_id(
        cls, gallery_task_id: str, client: "deeplabel.client.BaseClient"
    ) -> "GalleryTask":
        tasks = cls._from_search_params(
            params={"galleryTaskId": gallery_task_id}, client=client
        )
        if not len(tasks):
            raise InvalidIdError(
                f"No GalleryTask found for given gallery_task_id: {gallery_task_id}"
            )
        # since one videoTaskId corresponds to 1 and only 1 videoTask, return 0th videoTask
        return tasks[0]

    @classmethod
    def from_gallery_id(
        cls, gallery_id: str, client: "deeplabel.client.BaseClient"
    ) -> List["GalleryTask"]:
        return cls._from_search_params({"galleryId": gallery_id}, client)


    @property
    def detections(self) -> List["gallery_detections.Detection"]:
        """Get all the detections for the given videoTask

        Returns:
            List[deeplabel.infer.gallery.detections.Detection]: duh, isn't that self explanatory?
        """
        detections = gallery_detections.Detection.from_gallery_task_id(
            self.gallery_task_id, self.client
        )
        return detections

    @validate_arguments
    def insert_detections(
        self, detections: List[gallery_detections.Detection], chunk_size:int=500
    )->None:
        assert bool(detections), "detections in insert_detections method cannot be empty"

        # if not isinstance(detections[0], gallery_detections.Detection):
        #     assert isinstance(detections[0], dict), f"detections can either be deeplabel.infer.gallery.detections.Detection objects or corresponding dicts"
        #     detections = [gallery_detections.Detection(**det, client=None) for det in detections]


        count = 0
        for dets in chunk(detections, chunk_size):
            dets: List[gallery_detections.Detection]
            data = [
                json.loads(det.json(by_alias=True, exclude_none=True))
                for det in dets
            ]
            logger.debug(f"Pushing ({count} ~ {count+len(data)})/{len(detections)}")
            count += len(data)
            self.client.post("/image-detections", {"batch":True, "data": data, "galleryTaskId":self.gallery_task_id})
        logger.debug(
            f"Completed pushing {len(detections)} detections for galleryTaskId: {self.gallery_task_id}"
        )

    def update(self, progress:Optional[conint(ge=0,le=100)]=None, status:Optional[GalleryTaskStatus] = None)->"GalleryTask": #type: ignore
        data = {}
        if progress is not None:
            data['progress']=progress #type: ignore
        if status is not None:
            data['status']=status.value
        if not data:
            raise ValueError("No valid arguments passed to update. All args are None.")
        data['galleryTaskId'] = self.gallery_task_id

        updated_task = self.client.put('/gallery/tasks', json=data).json()['data']
        for key,val in updated_task.items():
            if key in self.__fields__:
                setattr(self, key,val)
        return self

def chunk(it:Iterable[Any], size:int):  # copied from https://stackoverflow.com/a/22045226/9504749
    it = iter(it)
    return iter(lambda: list(islice(it, size)), [])