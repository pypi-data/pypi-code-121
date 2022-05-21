from enum import Enum

class SeriliazeType(str,Enum):
    preprocess = "preprocess"
    postprocess = "postprocess"

    @staticmethod
    def has_value(item):
        return item in [v.value for v in SeriliazeType.__members__.values()]