from pydantic import BaseModel

from nwon_baseline.pydantic.path_to_write_pydantic_model import (
    path_to_write_pydantic_model,
)


def save_pydantic_model_instance_as_json(
    pydantic_model: BaseModel, file_path: str
) -> str:
    """
    Saves the Pydantic Model instance as a json file.

    Expects the file_path to end with '.json'.
    If the suffix is not json we take the basename of the file_path and attach .json
    """

    file_path = path_to_write_pydantic_model(file_path)

    with open(file_path, "w+", encoding="utf-8") as outfile:
        outfile.write(pydantic_model.json())

    return file_path
