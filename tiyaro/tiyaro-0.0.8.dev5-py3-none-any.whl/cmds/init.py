import os
import shutil
import subprocess
import tarfile
import re
import glob

import click
import requests

from ..api.status_update import update_status_init
from ..common.constants import *
from ..common.utils import failed, get_tiyaro_api_key, success, warn
from ..handler.cli_state import get_model_name_with_suffix, save_model_metadata, get_model_framework


@click.command()
@click.option('-f', '--force', is_flag=True, default=False, help=INIT_HELP)
@click.option('-v', '--verbose', is_flag=True, default=False, help=VERBOSE_HELP)
def init(force, verbose):
    """
    - Initializes model repo for Tiyaro Push
    """
    get_tiyaro_api_key()
    validate_ok_to_init(force, verbose)

    name = get_name(verbose)
    framework = get_framework(verbose)
    clazz = get_model_class(verbose)
    save_model_metadata(name, framework, clazz, verbose)
    update_status_init(get_model_name_with_suffix(), get_model_framework())

    if framework == 'pytorch':
        get_pytorch_templates(clazz, verbose)
        success(
            f'Created {TIYARO_HANDLER_DIR}, {HANDLER_MODEL_MODEL_TEST_FILE} templates successfully !')
    else:
        warn('Thank you for your interest in trying Tiyaro Cli !  Currently, only pytorch framework is supported.  Kindly reachout to Tiyaro Team.')
        subprocess.run(CMD_TIYARO_FORCE_CLEAN, shell=True)


def get_name(is_verbose):
    PATTERN = "[a-zA-Z_][a-zA-Z0-9_]*"
    while True:
        name = click.prompt('Please enter the name of your model', type=str)
        if re.fullmatch(PATTERN, name):
            break
        else:
            failed(f'Invalid name.  Must match pattern "{PATTERN}"\n')
    return name


def get_framework(is_verbose):
    while True:
        framework_opt = '\n 1\t Pytorch\n 2\t Tensorflow\n 3\t JAX\n 4\t Other -specify\n'
        option = click.prompt(
            f'Please enter the framework of your model {framework_opt} \t\t\t', type=str)
        option = option.casefold()

        if option in ['1', 'pytorch']:
            option = 'pytorch'
            break
        elif option in ['2', 'tensorflow']:
            option = 'tensorflow'
            break
        elif option in ['3', 'jax']:
            option = 'jax'
            break
        elif option == '4':
            failed(f'For option 4, please specify the framework name')
        else:
            break

        success(f'DEBUG - user selected framework is: {option}', is_verbose)
    return option


def get_model_class(is_verbose):
    while True:
        model_type_opt = f'\n 1\t {CLASS_IMAGE_CLASSIFICATION}\n 2\t {CLASS_TEXT_CLASSIFICATION}\n 3\t Other -{CLASS_CUSTOM}\n'
        option = click.prompt(
            f'Please enter the model type {model_type_opt} \t\t\t', type=str)
        option = option.casefold()

        if option in ['1', CLASS_IMAGE_CLASSIFICATION]:
            option = CLASS_IMAGE_CLASSIFICATION
            break
        elif option in ['2', CLASS_TEXT_CLASSIFICATION]:
            option = CLASS_TEXT_CLASSIFICATION
            break
        elif option in ['3', CLASS_CUSTOM]:
            option = CLASS_CUSTOM
            break
        else:
            failed(f'Please specify valid option')

        success(f'DEBUG - user selected class is: {option}', is_verbose)
    return option


def validate_ok_to_init(is_overwrite, is_verbose):
    __init_validate(is_overwrite, HANDLER_MODEL_MANIFEST_FILE)
    __init_validate(is_overwrite, HANDLER_MODEL_MODEL_HANDLER_FILE)
    __init_validate(is_overwrite, HANDLER_MODEL_MODEL_TEST_FILE)


def __init_validate(is_overwrite, file):
    if (os.path.isfile(file)):
        if not is_overwrite:
            warn(f"{file} already exists.  To force init kindly use 'tiyaro init -f' ")
            exit(-1)
        else:
            subprocess.run(CMD_TIYARO_FORCE_CLEAN, shell=True)


def get_pytorch_templates(clazz, is_verbose):
    success('Fetching tiyaro pytorch handler templates...')
    token = get_tiyaro_api_key()
    resp = requests.get(
        f'{PUSH_SUPPORT_FILES_ENDPOINT}/{ARTIFACTS_FILE_NAME}',
        headers={
            'Authorization': token
        })
    if resp.status_code == 200:
        template_url = resp.content
    else:
        failed(resp.status_code)
        failed(resp.content)
        failed(
            f'Unable to get templates URL.  Is your {TIYARO_API_KEY} still valid ?')
        exit(-1)

    os.makedirs(ARTIFACTS_DOWNLOAD_DIR)
    downloaded_artifact = f'{ARTIFACTS_DOWNLOAD_DIR}/ARTIFACTS_FILE_NAME'

    resp = requests.get(template_url, stream=True)
    if resp.status_code == 200:
        with open(downloaded_artifact, 'wb') as f:
            f.write(resp.raw.read())
    else:
        failed(
            f'Unable to get templates.  Is your {TIYARO_API_KEY} still valid ?')
        exit(-1)

    def members(tf, sub_folder):
        l = len(sub_folder)
        for member in tf.getmembers():
            if member.path.startswith(sub_folder):
                member.path = member.path[l:]
                yield member

    tar = tarfile.open(downloaded_artifact)
    tar.extractall(path=TIYARO_HANDLER_DIR,
                   members=members(tar, ARTIFACTS_FILES_DIR))
    tar.close()  # close before rmtree, some filesystems (nfs) may fail deleting dir with open files
    filter_class_specific_templates(clazz, is_verbose)
    # move test file to project root for tiyaro test
    shutil.move(f'{TIYARO_HANDLER_DIR}/{HANDLER_MODEL_MODEL_TEST_FILE}',
                f'{HANDLER_MODEL_MODEL_TEST_FILE}')
    shutil.rmtree(ARTIFACTS_DOWNLOAD_DIR)


def filter_class_specific_templates(clazz, is_verbose):
    to_rename = class_handler_map[clazz]
    old_name = to_rename
    sub_str = os.path.splitext(os.path.basename(to_rename))[0]
    to_rename = to_rename.replace(sub_str, MODEL_HANDLER)
    warn(
        f'DEBUG - for class: {clazz} renaming template : {old_name} to {to_rename}', is_verbose)
    os.rename(old_name, to_rename)
    
    for f in glob.glob(HANDLER_MODEL_CLASS_TEMPLATES_PATTERN):
        warn(f'DEBUG - deleting {f}', is_verbose)
        os.remove(f)
