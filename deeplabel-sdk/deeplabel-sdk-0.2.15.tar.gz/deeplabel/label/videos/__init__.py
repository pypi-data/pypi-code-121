"""
Module to get videos data
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import Field
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from pydantic import validator
import deeplabel.label.videos.frames
import deeplabel.label.videos.detections
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
import yarl
import os
from deeplabel.exceptions import DeeplabelValueError


class _VideoResolution(MixinConfig):
    height: int
    width: int


class _VideoFormat(MixinConfig):
    url: str
    resolution: Optional[_VideoResolution] = None
    extension: Optional[str] = None
    fps: Optional[float] = None
    file_size: Optional[float] = None


class _VideoUrl(MixinConfig):
    source: Optional[_VideoFormat]
    res360: Optional[_VideoFormat] = Field(None, alias="360P")
    res480: Optional[_VideoFormat] = Field(None, alias="480P")
    res720: Optional[_VideoFormat] = Field(None, alias="720P")
    res1080: Optional[_VideoFormat] = Field(None, alias="1080P")
    res1440: Optional[_VideoFormat] = Field(None, alias="1440P")
    res2160: Optional[_VideoFormat] = Field(None, alias="2160P")


class _TaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    HOLD = 'HOLD'
    RETRY = 'RETRY'
    REDO = 'REDO'


class _BaseStatus(MixinConfig):
    status: _TaskStatus
    start_time: float
    end_time: float
    error: Optional[str] = None


class _InferenceStatus(_BaseStatus):
    dl_model_id: Optional[str]
    progress: float


class _LabelVideoStatus(MixinConfig):
    download: _BaseStatus
    assign_resources: _BaseStatus
    extraction: _BaseStatus
    frames_extraction: _BaseStatus
    inference: _InferenceStatus
    label: _BaseStatus
    review: _BaseStatus
    labelling: _BaseStatus


class _ExtractionPoint(MixinConfig):
    labelling_fps: float
    start_time: float
    end_time: float


class Video(DeeplabelBase):
    video_id: str
    title:Optional[str]
    project_id: str
    input_url: str
    video_urls: Optional[_VideoUrl]
    video_url: Optional[str] # videoUrls.source.url if exists else videoUrl is used for legacy support
    thumbnail_url: Optional[str]
    status: _LabelVideoStatus
    extraction_points: List[_ExtractionPoint]
    duration: Optional[float]
    video_fps: Optional[float]
    labelling_fps: int

    @validator('video_url', always=True)
    def validate_url(cls, value, values): #type: ignore
        """
        Validate that either video_url or video_urls.source.url exists
        Since videoUrl can't be updated anymore, since it's deprecated,
        first check if videoUrls.source.url exists, and use that,
        else look for videoUrl
        Refer https://github.com/samuelcolvin/pydantic/issues/832#issuecomment-534896056
        """
        # video_urls.source.url
        try:
            source_url:str = values.get('video_urls',{}).source.url #type: ignore
        except:
            # should have either of the two
            # If video_url key is empty
            if isinstance(value, str):
                return value
            raise DeeplabelValueError(f"Video {values['video_id']} neither has video_url nor video_urls.source.url")
        # set video_url = video_urls.source.url
        return source_url

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Video"]:
        resp = client.get("/projects/videos", params=params)
        videos = resp.json()["data"]["videos"]
        videos = [cls(**video, client=client) for video in videos]
        return videos # type: ignore
    
    @classmethod
    def from_video_id(cls, video_id:str, client:'deeplabel.client.BaseClient')->"Video":
        videos = cls._from_search_params({"videoId": video_id}, client)
        if not len(videos):
            raise InvalidIdError(
                f"Failed to fetch video with videoId  : {video_id}"
            )
        # since videoId should fetch only 1 video, return that video instead of a list
        return videos[0]

    @property
    def ext(self):
        """Extenion of the video, deduced from path/name"""
        return os.path.splitext(yarl.URL(self.video_url).name)[-1]


    @property
    def detections(self):
        """Get Detections of the video"""
        return deeplabel.label.videos.detections.Detection.from_video_id(
            self.video_id, self.client
        )

    @property
    def frames(self):
        """Get Detections of the video"""
        return deeplabel.label.videos.frames.Frame.from_video_id(
            self.video_id, self.client
        )
