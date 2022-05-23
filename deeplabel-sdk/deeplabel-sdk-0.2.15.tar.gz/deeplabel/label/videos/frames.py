from typing import Any, List, Optional, Dict

from deeplabel.basemodel import DeeplabelBase, MixinConfig
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
import deeplabel.label.videos.detections as detections

class FrameResolution(MixinConfig):
    width:int
    height:int

class Frame(DeeplabelBase):
    displayed: bool
    review_comment:Optional[str]
    name:str
    number:int
    is_deleted:bool
    parent_folder_id:Optional[str]
    resolution:FrameResolution
    video_id: str
    frame_id: str
    frame_url:str
    point_in_time:float
    detections:List[detections.Detection]
    assignee:Optional[str]

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Frame"]:
        """Make a get request for detections using the passed params. This
        is a private method used internally by other class methods

        Returns:
            List[Detection]: Returns a list of Detection objects
        """
        resp = client.get("/projects/videos/frames", params=params)
        detections = resp.json()["data"]["frames"]
        # don't check for empty list in this generic class method. returns empty list if no detections were found
        detections = [cls(**det, client=client) for det in detections]
        return detections

    @classmethod
    def from_frame_id(cls, frame_id: str, client: "deeplabel.client.BaseClient"):
        frames = cls._from_search_params({"frameId": frame_id}, client)
        if not len(frames):
            raise InvalidIdError(
                f"Failed to fetch frame with frameId  : {frame_id}"
            )
        # since detectionId should fetch only 1 detection, return that detection instead of a list
        return frames[0]

    @classmethod
    def from_video_id(cls, video_id: str, client: "deeplabel.client.BaseClient"):
        return cls._from_search_params({"videoId": video_id, 'limit':'-1'}, client)