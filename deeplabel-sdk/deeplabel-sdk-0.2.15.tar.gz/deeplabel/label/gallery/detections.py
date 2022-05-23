
from enum import Enum
from typing import Any, List, Optional, Dict
from dataclasses import dataclass

from pydantic import Field, parse_obj_as, BaseModel
from deeplabel.basemodel import DeeplabelBase, MixinConfig
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.types.bounding_box import BoundingBox
from deeplabel.types.polygon import Point, Polygon
from deeplabel.label.labels import DetectionLabel


class ImageDetectionType(Enum):
    bounding_box = "image_bounding_box"
    polygon = "image_polygon"
    classification = "image_classification"

class Detection(DeeplabelBase):
    detection_id: Optional[str]
    is_reviewed: Optional[bool]
    type: ImageDetectionType
    bounding_box: Optional[BoundingBox]
    polygon: Optional[Polygon]
    label_id: DetectionLabel = Field(alias='label')


    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Detection"]:
        """Make a get request for detections using the passed params. This
        is a private method used internally by other class methods

        Returns:
            List[Detection]: Returns a list of Detection objects
        """
        resp = client.get("/projects/gallery/images/detections", params=params)
        detections = resp.json()["data"]["detections"]
        # don't check for empty list in this generic class method. returns empty list if no detections were found
        detections = [cls(**det, client=client) for det in detections]
        return detections

    @classmethod
    def from_detection_id(cls, detection_id: str, client: "deeplabel.client.BaseClient"):
        """Get the Detection object for a certail detection_id

        Args:
            detection_id (str): detection Id to search for
            client (deeplabel.client.BaseClient): client to call the api from

        Raises:
            InvalidIdError: If no detections are returned, raise InvalidIdError

        Returns:
            Detection: returns a Detection object or raises InvalidIdError if not found
        """
        detections = cls._from_search_params({"detectionId": detection_id}, client)
        if not len(detections):
            raise InvalidIdError(
                f"Failed to fetch detections with detectionId  : {detection_id}"
            )
        # since detectionId should fetch only 1 detection, return that detection instead of a list
        return detections[0]

    @classmethod
    def from_image_id(
        cls, image_id: str, client: "deeplabel.client.BaseClient"
    ) -> List["Detection"]:
        """Get all the detection of a videoTaskId

        Returns:
            List[Detection]: List of detections for the given videoTaskId
        """
        return cls._from_search_params({"imageId": image_id}, client)
