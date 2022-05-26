import json
import os
import uuid

from ..common.constants import *
from ..common.utils import failed, success
from ..api.status_update import update_status_init

C_MODEL_NAME = 'model_name'
C_MODEL_NAME_SUFFIX = 'model_name_suffix'


def get_model_name_with_suffix():
    return '{}_{}'.format(get_model_name(), get_model_suffix())


def get_model_name():
    return _get_state(C_MODEL_NAME)


def get_model_suffix():
    return _get_state(C_MODEL_NAME_SUFFIX)


def get_model_framework():
    return _get_state(C_MODEL_FRAMEWORK)


def get_model_class():
    return _get_state(C_MODEL_TYPE)


def save_model_metadata(model_name, model_framework, clazz, is_verbose):
    state = _get_full_state()
    state[C_MODEL_NAME] = model_name
    state[C_MODEL_FRAMEWORK] = model_framework
    state[C_MODEL_TYPE] = clazz
    suffix = state.get(C_MODEL_NAME_SUFFIX, None)
    if not suffix:
        state[C_MODEL_NAME_SUFFIX] = __rand()
    _write_state(state)
    pass


def _validate_state_exists():
    if (not os.path.exists(TIYARO_INTERNAL_STATE_FILE)):
        failed(f'{TIYARO_INTERNAL_STATE_FILE} doesnot exist')
        exit(-1)


def _get_full_state():
    if (not os.path.exists(TIYARO_INTERNAL_STATE_FILE)):
        existing_state = {}
    else:
        with open(TIYARO_INTERNAL_STATE_FILE, "r") as f:
            existing_state = json.load(f)
    return existing_state


def _get_state(key):
    _validate_state_exists()
    state = _get_full_state()
    value = state[key]
    if not value and value.strip():
        failed(f'Invalid key: {key}, value: {value}')
        exit(-1)
    return value


def _write_state(state):
    if not os.path.isdir(TIYARO_INTERNAL_DIR):
        os.makedirs(TIYARO_INTERNAL_DIR)
    with open(TIYARO_INTERNAL_STATE_FILE, 'w+', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


def create_internal_dir(is_verbose):
    if not os.path.isdir(TIYARO_INTERNAL_DIR):
        os.makedirs(ARTIFACTS_DOWNLOAD_DIR)
    else:
        success(f'{TIYARO_INTERNAL_DIR} already exists', is_verbose)


def __rand(string_length=6):
    random = str(uuid.uuid4())
    return random[0:string_length]
