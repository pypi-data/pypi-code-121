from typing import Type

from pydantic import BaseModel

from nwon_baseline.pydantic.path_to_write_pydantic_model import (
    path_to_write_pydantic_model,
)


def save_pydantic_model_schema(pydantic_model: Type[BaseModel], file_path: str) -> str:
    """
    Saves the JSON schema for a Pydantic Model in a json file.

    Expects the file_path to end with '.json'.
    If the suffix is not json we take the basename of the file_path and attach .json
    """

    file_path = path_to_write_pydantic_model(file_path)

    with open(file_path, "w+", encoding="utf-8") as outfile:
        outfile.write(pydantic_model.schema_json())

    return file_path
