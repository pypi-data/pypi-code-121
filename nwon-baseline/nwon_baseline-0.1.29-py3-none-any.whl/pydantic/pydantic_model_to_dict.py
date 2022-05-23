import json

from pydantic import BaseModel

from nwon_baseline.typings import AnyDict


def pydantic_model_to_dict(model: BaseModel) -> AnyDict:
    return json.loads(model.json())


__all__ = ["pydantic_model_to_dict"]
