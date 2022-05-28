"""
Copyright (c) 2022 Philipp Scheer
"""


from typing import Union
from rockeet import logger
from rockeet.helper import Response, endpoint


def identify(fileId: Union[Response,str],
             profiles: list,
             scale: float = 1,
             sensitivity: float = 0.9,
             nms: float = 0.3,
             similarityThreshold: float = 0.363,
             extraSimilarityThreshold: float = 1.128,
             scores: bool = False, 
             **kwargs) -> Response:
    """Create a face profile for a person"""

    if isinstance(fileId, Response):
        fileId = fileId.unpack("fileId")["fileId"]

    for i in range(len(profiles)):
        profile = profiles[i]
        if isinstance(profile, Response):
            profiles[i] = profile.unpack("fileId")["fileId"]

    logger.info(f"identify people in {fileId} (out of {len(profiles)} possibilities")

    obj = { **kwargs,
            "fileId": fileId,
            "profiles": profiles,
            "sensitivity": sensitivity,
            "nms": nms,
            "similarityThreshold": similarityThreshold,
            "extraSimilarityThreshold": extraSimilarityThreshold,
            "scores": scores,
           }
    if scale is not None: obj["scale"] = scale

    return endpoint("/image/identify", obj)
