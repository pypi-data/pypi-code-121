"""
Module to get videotasks data
"""
from enum import Enum
from itertools import islice
from typing import Any, Iterable, List, Dict, Optional
import deeplabel.infer.graphs.graph_nodes
import deeplabel.infer.videos.detections
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from pydantic import Field, conint, validate_arguments, validator
from logging import getLogger
import json

logger = getLogger(__name__)


class VideoTaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    ABORTED = "ABORTED"
    FAILURE = "FAILURE"


class VideoTaskVideoId(MixinConfig):
    title: Optional[str]
    video_id: str


class TimePoint(MixinConfig):
    start_time: float
    end_time: float

    @validator("end_time")
    def validate_end_time(cls, v, values):  # type: ignore
        """Validate that end_time is >= start_time"""
        assert (
            v >= values["start_time"]
        ), f"end_time {v} must be >= start_time {values['start_time']}"
        return v  # type: ignore

    @classmethod
    def from_detections(
        cls,
        detections: List["deeplabel.infer.videos.detections.Detection"],
        ignore_thresh: float = 2,
    ) -> List["TimePoint"]:
        if not detections: return []
        assert (isinstance(detections, List) and isinstance(detections[0],
                deeplabel.infer.videos.detections.Detection)), \
                f"detections should be of type List[deeplabel.infer.videos.detections.Detection]"
        time_points = []
        time_arr = sorted(list(set([det.time for det in detections])))
        time_points = [{"startTime": time_arr[0], "endTime": time_arr[0],}]

        for time in time_arr:
            if time > time_points[-1]["endTime"] + ignore_thresh:
                time_points.append(
                    {"startTime": time, "endTime": time,}
                )
            else:
                time_points[-1]["endTime"] = time
        return [cls(**time_point) for time_point in time_points]


class GraphNodeAnnotation(MixinConfig):
    name: str
    graph_node_id: str


class VideoTask(DeeplabelBase):
    video_task_id: str
    video: VideoTaskVideoId = Field(..., alias='videoId')
    graph_id: str
    graph_node: GraphNodeAnnotation = Field(..., alias="graphNodeId")
    is_shown: bool
    status: VideoTaskStatus
    progress: int
    init_time_points: List[TimePoint]
    final_time_points: List[TimePoint]
    name: str

    @classmethod
    def _from_search_params(cls, params: Dict[str, str], client: "deeplabel.client.BaseClient") -> List["VideoTask"]:  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/videos/tasks", params=params)
        tasks = resp.json()["data"]["videoTasks"]
        # Checkout https://lidatong.github.io/dataclasses-json/#use-my-dataclass-with-json-arrays-or-objects
        tasks = [cls(**task, client=client) for task in tasks if task['name']!='EDIT']
        return tasks  # type: ignore

    @classmethod
    def from_video_task_id(
        cls, video_task_id: str, client: "deeplabel.client.BaseClient"
    ) -> "VideoTask":
        tasks = cls._from_search_params(
            params={"videoTaskId": video_task_id}, client=client
        )
        if not len(tasks):
            raise InvalidIdError(
                f"No VideoTask found for given video_task_id: {video_task_id}"
            )
        # since one videoTaskId corresponds to 1 and only 1 videoTask, return 0th videoTask
        return tasks[0]

    @classmethod
    def from_video_id(
        cls, video_id: str, client: "deeplabel.client.BaseClient"
    ) -> List["VideoTask"]:
        return cls._from_search_params({"videoId": video_id}, client)

    @property
    def detections(self) -> List["deeplabel.infer.videos.detections.Detection"]:
        """Get all the detections for the given videoTask

        Returns:
            List[deeplabel.infer.detections.Detection]: duh, isn't that self explanatory?
        """
        if hasattr(self, "_detections"):
            return self._detections
        self._detections = deeplabel.infer.videos.detections.Detection.from_video_task_id(
            self.video_task_id, self.client
        )
        return self._detections

    def insert_detections(
        self,
        detections: List["deeplabel.infer.videos.detections.Detection"],
        chunk_size: int = 500,
    ):
        self.client: "deeplabel.client.BaseClient"
        if not detections: return None
        assert (isinstance(detections, List) and isinstance(detections[0],
                deeplabel.infer.videos.detections.Detection)), \
                f"detections should be of type List[deeplabel.infer.videos.detections.Detection]"

        def chunk(
            it: Iterable[Any], size: int
        ):  # copied from https://stackoverflow.com/a/22045226/9504749
            it = iter(it)
            return iter(lambda: list(islice(it, size)), [])

        count = 0
        for dets in chunk(detections, chunk_size):
            dets: List[deeplabel.infer.videos.detections.Detection]
            data = [
                json.loads(det.json(by_alias=True, exclude_none=True))
                for det in dets
            ]
            logger.debug(f"Pushing ({count} ~ {count+len(data)})/{len(detections)}")
            count += len(data)
            self.client.post("/detections", {"data": data, "batch": True, "videoTaskId":self.video_task_id})
        logger.info(
            f"Completed pushing {len(detections)} detections for videoTaskId: {self.video_task_id}"
        )

    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def update(
        self,
        final_time_points: Optional[List[TimePoint]] = None,
        progress: Optional[conint(ge=0, le=100)] = None, #type:ignore
        status: Optional[VideoTaskStatus] = None,
    ):
        data = {}
        if final_time_points is not None:
            data["finalTimePoints"] = [
                tp.dict(by_alias=True) for tp in final_time_points
            ]
        if progress is not None:
            data["progress"] = progress #type: ignore
        if status is not None:
            data["status"] = status.value
        if not data:
            raise ValueError("No valid arguments passed to update. All args are None.")
        data["videoTaskId"] = self.video_task_id

        updated_task = self.client.put("/videos/tasks", json=data).json()["data"]
        for key, val in updated_task.items():
            if key in self.__fields__:
                setattr(self, key, val)
        return self
