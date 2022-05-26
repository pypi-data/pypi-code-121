import json
import os
import shutil

import click
import requests

from ..api.status_update import update_status_pushed
from ..handler.cli_state import get_model_name_with_suffix
from ..common.constants import *
from ..common.utils import (failed, get_model_endpoint, get_tiyaro_api_key,
                            success, warn, delete_test_venv, get_python_version)
from ..handler.cli_state import get_model_name_with_suffix, get_model_framework, get_model_class
from ..handler.tiyaro_test_state import get_test_state, is_test_attempted
from ..handler.utils import validate_handler_exists
from ..handler.model_manifest import get_pretrained_file_or_url, validate_manifest_mandatory_params
from ..version import __version__


@click.command()
@click.option('-f', '--force', is_flag=True, default=False, help=VERBOSE_HELP)
@click.option('-v', '--verbose', is_flag=True, default=False, help=VERBOSE_HELP)
def push(force, verbose):
    """
    - Pushes model repo to Tiyaro Infrastructure
    """
    do_push(force, verbose)


def push_model(tiyaro_jwt_token: str, is_verbose):
    tiyaro_model_name = get_model_name_with_suffix()
    tiyaro_model_version = MODEL_VERSION

    def tiyaro_get_name_reservation_record(api_token):
        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        resp = requests.get(url=NAME_RESERVATION_ENDPOINT, headers=headers)
        if resp.status_code not in (200, 201):
            failed(
                f"Failed to reserve namespace.  Error code on {NAME_RESERVATION_ENDPOINT}: STATUS {resp.status}, REASON {resp.content}")
            warn('Kindly reach out to Tiyaro Support Team')
            exit(-1)
        return json.loads(resp.content)

    tiyaro_model_vendor = tiyaro_get_name_reservation_record(tiyaro_jwt_token)[
        'vendor_name']

    # TODO - USING PYTHON
    os.system(f"mkdir -p {UPLOAD_ARTIFACT_DIR}")
    # os.system("cp ./.tiyaro-install/state.json ./build") TODO: MULTI MODELS
    os.system(
        f"git archive --output={UPLOAD_ARTIFACT_DIR}/{GIT_SNAPSHOT_FILE_NAME} HEAD .")

    pretrained_file_path = get_pretrained_file_or_url()
    name_with_ext = None
    if os.path.isfile(pretrained_file_path):
        name_with_ext = os.path.basename(pretrained_file_path)
        dest_file_path = f'{UPLOAD_ARTIFACT_DIR}/{name_with_ext}'
        success(
            f'DEBUG - copying pretrained file from: {pretrained_file_path} to {dest_file_path}', is_verbose)
        shutil.copyfile(pretrained_file_path, dest_file_path)

    package_for_upload_client(UPLOAD_ARTIFACT_DIR, tiyaro_model_name,
                              tiyaro_model_vendor, tiyaro_model_version, tiyaro_jwt_token, name_with_ext, is_verbose)

    success(
        f'\n***Uploaded {tiyaro_model_name} to be converted onto Tiyaro Infrastructure', is_verbose)
    return get_model_endpoint(tiyaro_model_vendor, tiyaro_model_version, tiyaro_model_name)


def package_for_upload_client(build_subdir, tiyaro_model_name, tiyaro_model_vendor, model_version, tiyaro_jwt_token, pretrained_file_name, is_verbose):
    tiyaro_test_state = get_test_state()
    # TODO: Also send git hash info
    manifest_json = {
        'tiyaro_job_descriptor': TIYARO_JOB_DESCRIPTOR,
        'env_TIYARO_PUSH_NAME_BASE': None,
        'model_name': tiyaro_model_name,
        'model_vendor': tiyaro_model_vendor,
        'version': model_version,
        'model_type': TIYARO_MODEL_TYPE,
        'pretrained_file_name': pretrained_file_name,
        'tiyaro_authorization_token': tiyaro_jwt_token,
        C_MODEL_FRAMEWORK: get_model_framework(),
        C_MODEL_CLASS: get_model_class(),
        C_TEST_INPUT: tiyaro_test_state.get(C_TEST_INPUT, None),
        C_TEST_OUTPUT: tiyaro_test_state.get(C_TEST_OUTPUT, None),
        C_TEST_USER_CONFIRMED: tiyaro_test_state.get(C_TEST_USER_CONFIRMED, False),
        'user_python_env': get_python_version(),
        'cli_version': __version__
    }

    # Need to decorate with some tensor-specific information
    # with signature input and output

    manifest_json_filename = '/'.join([build_subdir, JSON_MANIFEST_FILE_NAME])
    with open(manifest_json_filename, 'w') as fout:
        fout.write(json.dumps(manifest_json, indent=4))

    success('START - Tarballing the artifacts into a single file', is_verbose)
    os.system(f'tar cf - {build_subdir} | gzip > {FILE_TO_UPLOAD}')
    success('FINISH - Tarballing the artifacts into a single file', is_verbose)

    success('START - Requesting a presigned url for upload', is_verbose)
    response_presigned_request = requests.get(
        PRESIGNED_REQUEST_ENDPOINT,
        headers={
            'Authorization': tiyaro_jwt_token
        })
    if response_presigned_request.status_code == 401:
        failed(
            f'Token Authorization Error.  Is your {TIYARO_API_KEY} still valid ?')
        exit(-1)
    elif response_presigned_request.status_code != 200:
        failed(
            f'Failed to received the presigned url from API endpoint {PRESIGNED_REQUEST_ENDPOINT}.', is_verbose)
        exit(-1)

    response_presigned_request_json = response_presigned_request.json()
    url = response_presigned_request_json['post_url']
    data = response_presigned_request_json['post_data_required']
    bucket_name = url.split('//')[1].split('.')[0]
    bucket_key = data['key']
    # click.echo(f'INFO - Received a presigned for S3 bucket {bucket_name} and key {bucket_key}')
    success(f'FINISH - Received a presigned url for upload {url}', is_verbose)

    size_payload = os.path.getsize(FILE_TO_UPLOAD)
    success(
        f'START - Upload of payload size {str(round(size_payload / (1024 * 1024), 2))}MB to a presigned url')
    with open(FILE_TO_UPLOAD, 'rb') as test_file_to_upload:
        # the key supposed to be file may be
        files = {'file': test_file_to_upload}
        response_file_upload = requests.post(url, data=data, files=files)
    if response_file_upload.status_code != 204:
        failed(
            f'Failed to upload the {FILE_TO_UPLOAD} to presigned url')
        exit(-1)

    success(f'FINISH - Upload to a presigned url')
    os.remove(FILE_TO_UPLOAD)
    return bucket_name, bucket_key

# before pushing, clean unwanted tiyaro generated artifacts


def clean_tiyaro_generated(is_verbose):
    delete_test_venv(is_verbose)


def do_push(is_force_push, is_verbose):
    clean_tiyaro_generated(is_verbose)
    validate_handler_exists()
    validate_manifest_mandatory_params()

    if not is_force_push:
        test_attempted = is_test_attempted()
        if not test_attempted:
            warn("Did you try 'tiyaro test' to test your handler ?\n You can also use 'tiyaro push -f' to force push without testing")
            exit(-1)

    token = get_tiyaro_api_key()
    api = push_model(token, is_verbose)
    update_status_pushed(get_model_name_with_suffix())

    success('\n\nView status at:')
    success(STATUS_PAGE_URL)
    success('\nInference API:')
    success(api)
