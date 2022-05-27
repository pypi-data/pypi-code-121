import numpy as np
import tensorflow as tf

from pydantic import Field, validator
from typing_extensions import Literal
from typing import Tuple, ClassVar, Optional, Union
from brevettiai.data.image import ImageProcessor
from brevettiai.data import DataGeneratorMap


class AnnotationPooling(ImageProcessor, DataGeneratorMap):
    """Module for pooling annotations to smaller resolution"""
    type: Literal["AnnotationPooling"] = "AnnotationPooling"
    input_key: str = Field(default="annotation")
    output_key: str = Field(default="annotation")

    pooling_method: Literal["max", "average"] = Field(default="max")
    pool_size: Optional[Union[int, Tuple[int, int]]] = Field(default=None)

    pooling_algorithms: ClassVar[dict] = {
        "max": tf.keras.layers.MaxPool2D,
        "average": tf.keras.layers.AveragePooling2D
    }

    def __init__(self, **data):
        super().__init__(**data)
        if self.output_key is None:
            self.output_key = self.input_key

    @validator("pool_size", pre=True, allow_reuse=True)
    def validate_pool_size(cls, v, field):
        # If empty list return None
        return v if v else None

    @property
    def pooling_function(self):
        return self.pooling_algorithms[self.pooling_method]

    def process(self, annotation):
        return self.pooling_function(pool_size=self.pool_size)(annotation)

    def affine_transform(self, input_height, input_width):
        return np.array((
            (1/self.pool_size[0], 0, 0),
            (0, 1/self.pool_size[1], 0),
            (1, 0, 1),
        ))

    def __call__(self, x, *args, **kwargs):
        x[self.output_key] = self.process(x[self.input_key])
        return x
