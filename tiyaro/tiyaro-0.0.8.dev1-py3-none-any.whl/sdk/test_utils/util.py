import json
import os
import shutil

import requests
import validators
import yaml

from ...common.constants import CLASS_TEXT_CLASSIFICATION, KEYWORD_FROM_CONFIG, HANDLER_MODEL_MANIFEST_FILE, C_PRETRAINED_FILE_OR_URL, CLASS_CUSTOM, CLASS_IMAGE_CLASSIFICATION
from ...handler.tiyaro_test_state import save_input, save_output
from ...handler.cli_state import get_model_class

from ..base_handler import TiyaroBase

KEYWORD_FROM_CONFIG = 'from-config'
HANDLER_MODEL_MANIFEST_FILE = './tiyaro_handler/model_manifest.yml'
C_PRETRAINED_FILE_OR_URL = 'pretrained_model_url'


def get_pretrained_file_path(x):
    def local_file(x, err_msg):
        if os.path.isfile(x):
            return x
        else:
            raise ValueError(err_msg)

    if x == KEYWORD_FROM_CONFIG:
        # read from yaml
        # if url, download to /tmp and return path
        # if local path, return path
        with open(HANDLER_MODEL_MANIFEST_FILE, 'r') as file:
            contents = yaml.safe_load(file)
            value = contents[C_PRETRAINED_FILE_OR_URL]
            if (
                (value is None)
                or (not isinstance(value, str))
                or (not value.strip())
            ):
                raise ValueError(
                    f'Please set a valid model {C_PRETRAINED_FILE_OR_URL} in {HANDLER_MODEL_MANIFEST_FILE}')
            if validators.url(value):
                r = requests.get(value, stream=True)
                file_path = '/tmp/pre_trained.pth'
                print(
                    f'DOWNLOADING - pretrained file to {file_path} from URL: {value}')
                if r.status_code == 200:
                    with open(file_path, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                    print('DOWNLOAD - Done')
                    return file_path
                else:
                    raise RuntimeError(
                        f'Unable to download pretrained file from: {value}')
            else:
                return local_file(value, 'Expected valid local file path')

    return local_file(x, 'Expected valid local file path')


def _get_input_json(x):
    if os.path.isfile(x):
        with open(x, 'r') as f:
            return json.load(f)
    if isinstance(x, str):
        return json.loads(x)

    raise ValueError('Expected Valid JSON input string or file path')

def _get_input_image_classification(x):
    if os.path.isfile(x):
        with open(x, 'rb') as img:
            return img.read()
    
    raise ValueError('Expected path to valid image file')

def _get_input_image_classification(x):
    if isinstance(x, str):
        return x
    
    raise ValueError('Expected input string')

def get_input_by_class(x):
    clazz = get_model_class()
    if clazz == CLASS_CUSTOM:
        return _get_input_json(x)
    elif clazz == CLASS_IMAGE_CLASSIFICATION:
        return _get_input_image_classification(x)
    elif clazz == CLASS_TEXT_CLASSIFICATION:
        return _get_input_image_classification(x)

    raise ValueError(f'ERROR - cannot get input for unknown model-type: {clazz}')


def validate_and_save_test_input(handler: TiyaroBase, test_input):
    clazz = get_model_class()
    if clazz == CLASS_CUSTOM:
        if handler.input_schema:
            # we validate if schema is declared
            handler.input_schema().load(test_input)
            save_input(test_input)
            print(f'INPUT - Validation Done')
        else:
            print('WARN - Input schema not defined')
    elif clazz == CLASS_IMAGE_CLASSIFICATION:
        if not isinstance(test_input, (bytearray, bytes)):
            raise ValueError(f'ERROR - for model-type: {CLASS_IMAGE_CLASSIFICATION}, input must be of type: bytes or bytearray')
        save_input(test_input)
    elif clazz == CLASS_TEXT_CLASSIFICATION:
        if not isinstance(str):
            raise ValueError(
                f'ERROR - for model-type: {CLASS_TEXT_CLASSIFICATION}, input must be of type: {type("string")}')
        save_input(test_input)
    else:
        print(f'WARN - unknown model-type: {clazz}')

def validate_and_save_test_output(handler: TiyaroBase, test_output):
    clazz = get_model_class()
    if clazz == CLASS_CUSTOM:
        if handler.output_schema:
            # we validate if schema is declared
            handler.output_schema().load(test_output)
            save_output(test_output)
            print(f'OUTPUT - Validation Done')
        else:
            print('WARN - Output schema not defined')
    elif clazz == CLASS_IMAGE_CLASSIFICATION:
        if not isinstance(test_output, dict):
            raise ValueError(
                f'ERROR - for model-type: {CLASS_IMAGE_CLASSIFICATION}, output must be of type: {type({})}')
        save_output(test_output)
    elif clazz == CLASS_TEXT_CLASSIFICATION:
        if not isinstance(test_output, dict):
            raise ValueError(
                f'ERROR - for model-type: {CLASS_TEXT_CLASSIFICATION}, output must be of type: {type({})}')
        save_output(test_output)
    else:
        print(f'WARN - unknown model-type: {clazz}')
