from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic import StrictBool
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import ValidationError
from pydantic import conlist
from pydantic.error_wrappers import ErrorWrapper

from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseInstance
from superannotate_schemas.schemas.base import BaseMetadata
from superannotate_schemas.schemas.base import BaseModel
from superannotate_schemas.schemas.base import BboxPoints
from superannotate_schemas.schemas.base import INVALID_DICT_MESSAGE
from superannotate_schemas.schemas.base import NotEmptyStr
from superannotate_schemas.schemas.base import PointLabels
from superannotate_schemas.schemas.base import StrictNumber
from superannotate_schemas.schemas.base import StrictPointNumber
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.enums import AnnotationStatusEnum


class Attribute(BaseAttribute):
    name: NotEmptyStr
    group_name: NotEmptyStr = Field(alias="groupName")


class VideoType(str, Enum):
    EVENT = "event"
    BBOX = "bbox"
    POINT = "point"
    POLYGON = "polygon"
    POLYLINE = "polyline"


class MetaData(BaseMetadata):
    width: Optional[StrictInt]
    height: Optional[StrictInt]
    status: Optional[AnnotationStatusEnum]
    duration: Optional[StrictInt]
    error: Optional[StrictBool]


class BaseTimeStamp(BaseModel):
    timestamp: StrictInt
    attributes: Optional[List[Attribute]]


class BboxTimeStamp(BaseTimeStamp):
    points: BboxPoints


class PointTimeStamp(BaseTimeStamp):
    x: StrictNumber
    y: StrictNumber


class EventTimeStamp(BaseTimeStamp):
    pass


class InstanceMetadata(BaseInstance):
    type: VideoType
    start: StrictInt
    end: StrictInt

    class Config:
        fields = {"creation_type": {"exclude": True}}


class BBoxInstanceMetadata(InstanceMetadata):
    type: StrictStr = Field(VideoType.BBOX, const=True)
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")


class PolygonInstanceMetadata(InstanceMetadata):
    type: StrictStr = Field(VideoType.POLYGON, const=True)
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")


class PolylineInstanceMetadata(InstanceMetadata):
    type: StrictStr = Field(VideoType.POLYLINE, const=True)
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")


class PointInstanceMetadata(InstanceMetadata):
    type: StrictStr = Field(VideoType.POINT, const=True)
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")


class EventInstanceMetadata(InstanceMetadata):
    type: StrictStr = Field(VideoType.EVENT, const=True)


class BaseVideoInstance(BaseModel):
    metadata: InstanceMetadata
    id: Optional[str]
    type: VideoType
    locked: Optional[bool]
    timeline: Dict[float, BaseTimeStamp]


class BaseParameter(BaseModel):
    start: StrictInt
    end: StrictInt


class BboxParameter(BaseParameter):
    timestamps: conlist(BboxTimeStamp, min_items=2)


class PolygonParameter(BaseParameter):
    timestamps: conlist(StrictPointNumber, min_items=3)


class PolylineParameter(BaseParameter):
    timestamps: conlist(StrictPointNumber)


class PointParameter(BaseParameter):
    timestamps: conlist(PointTimeStamp, min_items=2)


class EventParameter(BaseParameter):
    timestamps: conlist(EventTimeStamp, min_items=2)


class BboxInstance(BaseModel):
    meta: BBoxInstanceMetadata
    parameters: conlist(BboxParameter, min_items=1)


class PointInstance(BaseModel):
    meta: PointInstanceMetadata
    parameters: conlist(PointParameter, min_items=1)


class PolygonInstance(BaseModel):
    meta: PolygonInstanceMetadata
    parameters: conlist(PolylineParameter, min_items=1)


class PolylineInstance(BaseModel):
    meta: PolylineInstanceMetadata
    parameters: conlist(PolylineParameter, min_items=1)


class EventInstance(BaseModel):
    meta: EventInstanceMetadata
    parameters: conlist(EventParameter, min_items=1)


ANNOTATION_TYPES = {
    VideoType.BBOX: BboxInstance,
    VideoType.EVENT: EventInstance,
    VideoType.POINT: PointInstance
}


class AnnotationInstance(BaseModel):
    __root__: Union[
        BboxInstance, EventInstance, PointInstance
    ]

    @classmethod
    def __get_validators__(cls):
        yield cls.return_action

    @classmethod
    def return_action(cls, values):

        try:
            meta = values.get("meta")
            if not meta:
                raise ValidationError(
                    [ErrorWrapper(ValueError("field required"), "meta")], cls
                )
            try:
                instance_type = meta["type"]
            except KeyError:
                raise ValidationError(
                    [ErrorWrapper(ValueError("field required"), "meta.type")], cls
                )
            return ANNOTATION_TYPES[instance_type](**values)
        except KeyError:
            raise ValidationError(
                [
                    ErrorWrapper(
                        ValueError(
                            f"invalid type, valid types are {', '.join(ANNOTATION_TYPES.keys())}"
                        ),
                        "meta.type",
                    )
                ],
                cls,
            )
        except TypeError as e:
            raise ValidationError(
                [ErrorWrapper(ValueError(INVALID_DICT_MESSAGE), "meta")], cls
            )


class VideoAnnotation(BaseModel):
    metadata: MetaData
    instances: Optional[List[AnnotationInstance]] = Field(list())
    tags: Optional[List[Tag]] = Field(list())
