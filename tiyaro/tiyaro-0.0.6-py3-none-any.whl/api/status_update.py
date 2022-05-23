import requests
import json

from ..common.constants import STATUS_UPDATE_ENDPOINT_PREFIX, TIYARO_API_KEY, MODEL_VERSION
from ..common.utils import get_tiyaro_api_key, failed
from ..version import __version__

C_STATUS_INIT = 'init'
C_STATUS_TEST_FAILED = 'test_failed'
C_STATUS_TEST_PASSED = 'test_passed'
C_STATUS_PUSH = 'pushed'
C_STATUS = 'status'
C_FRAMEWORK = 'framework'

STATUS_UPDATE_API = '{}/{}/{}'


def update_status_init(model_name, model_framework):
    _update_status(C_STATUS_INIT, model_name, model_framework)
    pass


def update_status_test_passed(model_name):
    _update_status(C_STATUS_TEST_PASSED, model_name)
    pass


def update_status_test_failed(model_name):
    _update_status(C_STATUS_TEST_FAILED, model_name)
    pass


def update_status_pushed(model_name):
    _update_status(C_STATUS_PUSH, model_name)
    pass


def _update_status(status, name, framework=None):
    url = STATUS_UPDATE_API.format(
        STATUS_UPDATE_ENDPOINT_PREFIX, name, MODEL_VERSION)
    token = get_tiyaro_api_key()
    headers = {
        'Authorization': f'Bearer {token}',
        'cli_version': __version__
    }
    body = {}
    body[C_STATUS] = status
    body[C_FRAMEWORK] = framework
    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code == 401:
        failed(
            f'Token Authorization Error.  Is your {TIYARO_API_KEY} still valid ?')
        exit(-1)
    if resp.status_code == 400:
        body = json.loads(resp.content)
        if body['code'] == 'UPGRADE_REQUIRED':
            failed(
                f'Please upgrade your tiyaro cli.  Supported version: {body["message"]}')
            exit(-1)
    if resp.status_code != 200:
        failed(f'Unable to udpate status: {resp.content}')
