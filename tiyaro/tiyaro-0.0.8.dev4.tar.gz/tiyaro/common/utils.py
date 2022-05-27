import os
import shutil
import platform

import click

from .constants import (INFERENCE_ENDPOINT_PREFIX, TIYARO_TEST_VENV_PATH,
                        TIYARO_API_KEY)


def wip():
    warn(f'** WORK IN PROGRESS **\n Please wait for new version release..')


def get_tiyaro_api_key():
    token = os.getenv(TIYARO_API_KEY, None)
    if token is None:
        failed(f'Please set {TIYARO_API_KEY} env var')
        exit(-1)
    return token


def get_model_endpoint(vendor, version, model):
    return f'{INFERENCE_ENDPOINT_PREFIX}/{vendor}/{version}/{model}'


def success(msg, is_verbose=True):
    if is_verbose:
        click.secho(msg, fg='green')


def failed(msg, is_verbose=True):
    if is_verbose:
        click.secho(msg, fg='red')


def warn(msg, is_verbose=True):
    if is_verbose:
        click.secho(msg, fg='yellow')


def delete_test_venv(is_verbose=True):
    if (os.path.isdir(TIYARO_TEST_VENV_PATH)):
        success(f'Cleaning up VENV: {TIYARO_TEST_VENV_PATH}', is_verbose)
        shutil.rmtree(TIYARO_TEST_VENV_PATH)


def get_python_version():
    return platform.python_version()
