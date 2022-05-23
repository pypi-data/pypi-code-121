import os

import yaml
import validators

from ..common.constants import HANDLER_MODEL_MANIFEST_FILE, MODEL_VERSION, C_PRETRAINED_FILE_OR_URL, C_REQUIREMENTS_FILE, C_MODEL_FILE_PATH
from ..common.utils import failed
from .utils import validate_model_manifest_file_exists


# TODO: reintroduce when we add support for version
# def get_model_version():
#     validate_model_manifest_file_exists()
#     return f'{MODEL_VERSION}'

# # use this only for getting value from manifest file
# def get_model_name():
#     validate_model_manifest_file_exists()
#     return _get_param('name')

def validate_manifest_mandatory_params():
    get_pretrained_file_or_url()
    get_requirements_file_path()
    validate_model_file_path()

def validate_model_file_path():
    validate_model_manifest_file_exists()
    file = _get_param(C_MODEL_FILE_PATH)
    if not os.path.isfile(file):
        failed(
            f'Invalid file path: {file} key:{C_MODEL_FILE_PATH} in {HANDLER_MODEL_MANIFEST_FILE}')
        exit(-1)

def get_pretrained_file_or_url():
    validate_model_manifest_file_exists()
    file_or_url = _get_param(C_PRETRAINED_FILE_OR_URL)
    if not validators.url(file_or_url) and not os.path.isfile(file_or_url):
        failed(
            f'Invalid file path or url: {file_or_url} key:{C_PRETRAINED_FILE_OR_URL} in {HANDLER_MODEL_MANIFEST_FILE}')
        exit(-1)
    return file_or_url

def get_requirements_file_path():
    validate_model_manifest_file_exists()
    path = _get_param(C_REQUIREMENTS_FILE)
    if not os.path.isfile(path):
        failed(
            f'Invalid file path: {path} key:{C_REQUIREMENTS_FILE} in {HANDLER_MODEL_MANIFEST_FILE}')
        exit(-1)
    return path


def _get_param(field):
    with open(HANDLER_MODEL_MANIFEST_FILE, 'r') as file:
        contents = yaml.safe_load(file)
        value = contents[field]
        if (
            (value is None)
            or (not isinstance(value, str))
            or (not value.strip())
        ):
            failed(
                f'Please set a valid model {field} in {HANDLER_MODEL_MANIFEST_FILE}')
        return value
