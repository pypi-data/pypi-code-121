import os
import tqdm
import sys

from typing import Callable, List, Dict

from pyDataverse.api import NativeApi, DataAccessApi
from easyDataverse.tools.utils import get_class
from easyDataverse.core.file import File
from easyDataverse.core.exceptions import (
    MissingCredentialsException,
    MissingURLException,
)


def download_from_dataverse(dataset, doi: str, lib_name: str, filedir: str):
    """Downloads a dataset from a Dataverse instance and initializes a Dataset object.

    Args:
        dataset (Dataset): Empty dataset to which will be written.
        lib_name (str): INTERNAL. Used to derive the underlying generated API.
    """

    # Get environment variables
    try:
        DATAVERSE_URL = os.environ["DATAVERSE_URL"]

    except KeyError:
        raise MissingURLException

    try:
        API_TOKEN = os.environ["DATAVERSE_API_TOKEN"]
    except KeyError:
        raise MissingCredentialsException

    # Intialize the pyDataverse instance to fetch the dataset
    api = NativeApi(DATAVERSE_URL, API_TOKEN)
    data_api = DataAccessApi(DATAVERSE_URL, API_TOKEN)

    # Download the dataset and retrieve the field data
    dv_dataset = api.get_dataset(doi)
    setattr(dataset, "p_id", doi)
    json_data = dv_dataset.json()["data"]["latestVersion"]["metadataBlocks"]

    # Build new mapping
    data = {}

    for block_name, block in json_data.items():

        module_path = f".metadatablocks.{block_name[0].lower() + block_name[1::]}"

        _, module = get_class(module_path, lib_name)

        fields = block["fields"]
        data = {}

        for field in fields:
            parser_fun = field_parser_factory(field["typeClass"])
            data.update(parser_fun(field, module))

        # Initialize the module
        dataset.add_metadatablock(module.parse_obj(data))

    # Add all files present in the dataset
    files_list = dv_dataset.json()["data"]["latestVersion"]["files"]
    download_files(data_api, dataset, files_list, filedir)

    return dataset


def field_parser_factory(field_type: str) -> Callable:
    """Manages the parsing of specific fields"""

    mapping = {
        "compound": parse_compound,
        "primitive": parse_primitive,
        "controlledVocabulary": parse_primitive,
    }

    return mapping[field_type]


def parse_primitive(field: dict, module):
    """Parses a primtive field by checking the API schema."""

    # Get module properties
    properties = module.schema()["properties"]

    return {
        attr_name: field["value"]
        for attr_name, property in properties.items()
        if property["typeName"] == field["typeName"]
    }


def parse_compound(field: dict, module):
    """Parses a compound field by checking the module schema to a list of JSON objects"""

    # Retrieve the definitions from the module schema
    compound_name, field_mapping = _get_compound_definitions(module, field["typeName"])

    return {
        compound_name: [
            {
                field_mapping[type_name]: sub_field["value"]
                for type_name, sub_field in obj.items()
            }
            for obj in field["value"]
        ]
    }


def _get_compound_definitions(module, type_name: str):
    """Retrieves the compound definitions found in the module schema."""

    for obj_name, property in module.schema()["properties"].items():
        compound_name = property["typeName"]

        if compound_name == type_name:

            definition_name = property["items"]["$ref"].split("/")[-1]
            definition = module.schema()["definitions"][definition_name]["properties"]

            # Create a mapping from typeName to actual attribute name
            mapping = {
                field["typeName"]: attr_name for attr_name, field in definition.items()
            }

            return obj_name, mapping

    raise NameError(
        f"Field with typeName {type_name} is not defined in module {module.__name__}"
    )


def download_files(
    data_api: DataAccessApi, dataset, files_list: List[Dict], filedir: str
) -> None:
    """Downloads and adds all files given in the dataset to the Dataset-Object"""

    # Set up the progress bar
    files_list = tqdm.tqdm(files_list, file=sys.stdout)
    files_list.set_description(f"Downloading data files")

    for file in files_list:

        # Get file metdata
        filename = file["dataFile"]["filename"]
        file_pid = file["dataFile"]["id"]

        description = file["dataFile"].get("description")
        directory_label = file.get("directoryLabel")

        # Get the content
        response = data_api.get_datafile(file_pid)

        if response.status_code != 200:
            raise FileNotFoundError(f"No content found for file {filename}.")

        # Create local path for later upload
        if directory_label:
            filename = os.path.join(directory_label, filename)

        local_path = os.path.join(filedir, filename)

        # Write content to local file
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(response.content)

        # Create the file object
        datafile = File(
            filename=filename,
            description=description,
            local_path=local_path,
            file_pid=file_pid,
        )

        dataset.files.append(datafile)
