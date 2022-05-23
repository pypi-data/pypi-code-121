from dataclasses import dataclass
from typing import Optional
from deeplabel.basemodel import MixinConfig
from deeplabel.types.bounding_box import BoundingBoxWithNumber as BoundingBox


class Sequence(MixinConfig):
    number:int
    bounding_box:Optional[BoundingBox]