"""
Copyright (c) 2022 Philipp Scheer
"""


from rockeet.helper import Response, endpoint


def list() -> Response:
    """Delete a file given its `fileId`"""
    return endpoint(f"/files", body={}, method="get").result
