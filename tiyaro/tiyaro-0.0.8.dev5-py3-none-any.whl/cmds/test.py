import subprocess
import venv
import os

import click

from ..api.status_update import (update_status_test_failed,
                                 update_status_test_passed)
from ..handler.cli_state import get_model_name_with_suffix
from ..common.constants import (HANDLER_MODEL_MANIFEST_FILE,
                                HANDLER_MODEL_MODEL_TEST_FILE, TEST_COMMAND_ARG_INPUT, TEST_COMMAND_ARG_OUTPUT, TEST_COMMAND_ARG_PRETRAINED, VERBOSE_HELP, TIYARO_TEST_VENV_PATH, KEYWORD_FROM_CONFIG)
from ..common.utils import failed, success, delete_test_venv
from ..handler.model_manifest import get_requirements_file_path, validate_manifest_mandatory_params
from ..handler.tiyaro_test_state import save_user_confirmed
from ..handler.utils import (validate_handler_exists,
                             validate_handler_test_file_exists)


@click.command()
@click.option('-p', TEST_COMMAND_ARG_PRETRAINED, required=False, help=f'pretrained_file path or url.  default is value from {HANDLER_MODEL_MANIFEST_FILE}')
@click.option('-i', TEST_COMMAND_ARG_INPUT, required=True, help=f'Valid input string or file path that contains input in expected format for your model-type')
@click.option('-o', TEST_COMMAND_ARG_OUTPUT, required=False, help=f'Inference output file - saves inference output to the specified file')
@click.option('-dv', '--delvenv', is_flag=True, default=True, help=f'Delete venv after each tiyaro test run, default=True')
@click.option('-v', '--verbose', is_flag=True, default=False, help=VERBOSE_HELP)
def test(pretrained, input, output, delvenv, verbose):
    """
    - Test model locally & validate expected input output formats
    """
    do_test(pretrained, input, output, delvenv, verbose)


def do_test(pretrained, input, output_file, is_del_venv, is_verbose):
    validate_handler_exists()
    validate_handler_test_file_exists()
    validate_manifest_mandatory_params()

    requirements_file_path = get_requirements_file_path()

    success(f'Creating VENV: {TIYARO_TEST_VENV_PATH}')
    venv.create(TIYARO_TEST_VENV_PATH, with_pip=True)

    os.system(
        f'{TIYARO_TEST_VENV_PATH}/bin/pip3 install -r {requirements_file_path}')

    if not pretrained:
        pretrained = KEYWORD_FROM_CONFIG
    
    # input can have space so added quotes
    p = subprocess.run(
        f'{TIYARO_TEST_VENV_PATH}/bin/python {HANDLER_MODEL_MODEL_TEST_FILE} {TEST_COMMAND_ARG_PRETRAINED} {pretrained} {TEST_COMMAND_ARG_INPUT}="{input}" {TEST_COMMAND_ARG_OUTPUT} {output_file}', shell=True)

    if is_del_venv:
        delete_test_venv(is_verbose)

    if p.returncode == 0:
        while True:
            yes_or_no = click.prompt(
                'Is this your expected output (Y/n) ?', type=str)
            if yes_or_no in ["Y", 'n']:
                break
        if yes_or_no == "Y":
            save_user_confirmed(True)
        else:
            save_user_confirmed(False)

        update_status_test_passed(get_model_name_with_suffix())
        success('Test successful !  You can push your model now.')
    else:
        update_status_test_failed(get_model_name_with_suffix())
        failed('Test failed !')
