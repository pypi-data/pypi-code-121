"""
Copyright (c) 2022 Philipp Scheer
"""


from typing import Union
from rockeet import logger
from rockeet.helper import Response, endpoint


def person(profile: Union[Response,dict], name: str, metadata: dict = {}, fileId: str = None, **kwargs) -> Response:
    """Create a face profile for a person"""

    if isinstance(profile, Response):
        allowedEndpoints = ["/image/faces"]
        assert profile.sUrl in allowedEndpoints, f"a face profile can only be created from one of the following endpoints: {', '.join(allowedEndpoints)}"
        # when the request comes directly from /image/faces, use the fileId in the request
        fileId = profile.sBody.get("fileId")
        profile = profile.result
        assert len(profile) > 0, "no face detected"
        profile = profile[0]
    else:
        logger.warn(f"you're importing your own profile\nthis is not recommended and might lead to weird results")

    assert fileId is not None, f"no file to create a face profile with.\nuse either the /image/faces endpoint directly or store the values returned by the endpoint and pass them using the profile parameter and specify the right fileId"

    logger.info(f"creating a face profile of {name} using file {fileId}")

    return endpoint("/image/person", {
        **kwargs,
        "fileId": fileId,
        "name": name,
        "metadata": metadata,
        "profile": profile["profile"]
    })
