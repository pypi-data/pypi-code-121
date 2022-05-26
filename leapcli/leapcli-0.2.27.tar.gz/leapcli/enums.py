# pylint: disable=invalid-name

from enum import Enum


class ResourceEnum(Enum):
    secret = "secret"


class ModelType(Enum):
    h5 = "H5_TF2"
    onnx = "ONNX"
