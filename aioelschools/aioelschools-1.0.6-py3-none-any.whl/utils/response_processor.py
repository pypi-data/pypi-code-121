from typing import Type

from pydantic import BaseModel

from ..errors import (
    APIError
)


async def check_response(status, response: dict, datatype: Type[BaseModel]):
    if status == 200 and response["status"] == "ok":
        return datatype(**response)

    exception = APIError[int(response["error"]["code"])](response["error"]["description"])
    raise exception
