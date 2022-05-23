from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from deeplabel.basemodel import DeeplabelBase
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.label.gallery.detections import Detection, ImageDetectionType
from . import detections
import logging
logger = logging.getLogger(__name__)

class _ImageResolution(BaseModel):
    height:int
    width:int

class Image(DeeplabelBase):
    image_id: str
    gallery_id:str
    image_url:str
    assignee:Optional[str]
    project_id:str
    resolution:_ImageResolution
    name:str
    displayed:bool
    parentFolderId:Optional[str]
    detections:List[detections.Detection]
    is_deleted:bool
    parent_folder_id:Optional[str]
    project_id: str

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Image"]:
        resp = client.get("/projects/gallery/images", params=params)
        images = resp.json()["data"]["images"]
        images = [cls(**image, client=client) for image in images]
        return images
    
    @classmethod
    def from_gallery_id(cls, gallery_id:str, client:"deeplabel.client.BaseClient")->List["Image"]:
        return cls._from_search_params({"galleryId":gallery_id}, client=client)
    
    @classmethod
    def from_image_id(cls, image_id: str, client: "deeplabel.client.BaseClient"):
        images = cls._from_search_params({"imageId": image_id}, client)
        if not len(images):
            raise InvalidIdError(
                f"Failed to fetch image with imageId  : {image_id}"
            )
        # since detectionId should fetch only 1 detection, return that detection instead of a list
        return images[0]
    
    def insert_detections(self, detections:List[Detection]):
        final_detections = []
        for d in detections:
            detection = {
            "labelId":d.label_id.label_id,
            "galleryId":self.gallery_id,
            "type":d.type.value,
            "imageId":self.image_id,
            "projectId":self.project_id
            }
            if d.type == ImageDetectionType.bounding_box:
                detection['boundingBox'] = d.bounding_box.dict()
                detection['type']='bounding_box'
            if d.type == ImageDetectionType.polygon:
                detection['type']='polygon'
                detection['polygon'] = d.polygon.dict()
            final_detections.append(detection)
        self.client:"deeplabel.client.BaseClient"
        resp = self.client.post("/projects/gallery/images/detections/mixed", {"imageId":self.image_id, "insertData":final_detections, "deleteData":[],"updateData":[]})
        assert resp.status_code == 200, f"Failed to insert detections in deeplabel for imageId {self.image_id}. {resp.text}"
        logger.debug(f"Completed inserting {len(final_detections)} detections for imageId {self.image_id}, galleryId {self.gallery_id}, projectId {self.project_id}")

    @classmethod
    def create(cls, url:str, gallery_id:str, height:int, width:int, name:str, client:"deeplabel.client.BaseClient", displayed:bool=True)->"Image":
        resp = client.post("/projects/gallery/images", {
            "imageUrl":url,
            "galleryId":gallery_id,
            "resolution":{
                "height":height,
                "width":width,
            },
            "name":name,
            "displayed":displayed
        })
        if resp.status_code != 200:
            logger.error(f"Failed creating image: {resp.text}")
        return cls(**resp.json()['data'], client=client)
