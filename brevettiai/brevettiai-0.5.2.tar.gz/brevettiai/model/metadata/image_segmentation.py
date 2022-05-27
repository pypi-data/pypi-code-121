import cv2
from pydantic import constr, root_validator, Field
from typing import List, Tuple, Optional
from .metadata import ModelMetadata
from brevettiai.data.image import ImagePipeline, ImageLoader, AnnotationLoader
from brevettiai.data.image.annotation_pooling import AnnotationPooling
from brevettiai.data.image.multi_frame_imager import MultiFrameImager

import numpy as np
from base64 import b64encode, b64decode


class Base64Image(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def validate_type(cls, val):
        if isinstance(val, str):
            return cv2.imdecode(np.frombuffer(b64decode(val), np.uint8), -1).view(Base64Image)
        return val.view(Base64Image)

    def __repr__(self):
        status, buf = cv2.imencode(".png", self)
        assert status
        return b64encode(buf).decode()


class ImageSegmentationModelMetadata(ModelMetadata):
    """
    Metadata for an Image segmentation model
    """
    producer: constr(regex="^ImageSegmentation.*$") = "ImageSegmentation"

    # Info
    classes: List[str]
    suggested_input_shape: Tuple[int, int] = Field(description="height, width of image suggested for input")

    # Training
    image_loader: ImageLoader
    multi_frame_imager: Optional[MultiFrameImager]

    annotation_loader: AnnotationLoader

    # augmentation: Optional[ImageAugmenter]

    annotation_pooling: Optional[AnnotationPooling]

    # Documentation
    example_image: Optional[Base64Image] = Field(description="Base64 encoded image file containing example image")

    class Config:
        json_encoders = {
            Base64Image: repr
        }

    @root_validator(pre=True, allow_reuse=True)
    def prepare_input(cls, values):
        if values.get("producer") == "ImageSegmentation":
            if "classes" not in values:
                values["classes"] = values["image_pipeline"]["segmentation"]["classes"]
            if "suggested_input_shape" not in values:
                values["suggested_input_shape"] = values["tile_size"]
            if "image_pipeline" in values:
                ip = ImagePipeline.from_config(values.pop("image_pipeline"))

                values["image_loader"] = ip.to_image_loader()
                if ip.segmentation is not None:
                    values["annotation_loader"] = AnnotationLoader(
                        mapping=ip.segmentation.mapping,
                        classes=ip.segmentation.classes)
        return values
