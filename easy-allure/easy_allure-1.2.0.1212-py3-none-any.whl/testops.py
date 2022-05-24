import argparse
import os
from typing import Dict

from .allurectl import install_allurectl
from .exceptions import ScriptException
from .helpers import run_cmd
from .logger import get_logger

LOGGER = get_logger()


class AllureTestops():
    def __init__(self, platform: str = None) -> None:
        self.platform = platform
        self.executable = install_allurectl(self.platform)

    def create_launch(self, launch_name: str) -> str:
        cmd = '{} launch create --launch-name {} ' \
              '--no-header --format ID' \
              .format(self.executable, launch_name)
        try:
            launch_id, _ = run_cmd(cmd)
        except RuntimeError as err:
            errMessage = 'Failed to create launch: {}'.format(err)
            raise ScriptException(errMessage)

        launch_id = launch_id.strip()
        if not launch_id:
            errMessage = 'Failed to receive launch id from allurectl, ' \
                         'empty launch_id received from allurectl'
            raise ScriptException(errMessage)

        return launch_id

    def upload_launch(self, reports_path: str, launch_id: str) -> None:
        cmd = '{} upload {} --launch-id {}' \
            .format(self.executable, reports_path, launch_id)
        try:
            run_cmd(cmd)
        except RuntimeError as err:
            errMessage = 'Failed to upload launch: {}'.format(err)
            raise ScriptException(errMessage)

    def close_launch(self, launch_id: str) -> None:
        cmd = '{} launch close {}'.format(self.executable, launch_id)
        try:
            run_cmd(cmd)
        except RuntimeError as err:
            errMessage = 'Failed to close launch: {}'.format(err)
            raise ScriptException(errMessage)


def send_to_testops(testops_obj, parsed_args: argparse.Namespace) -> int:
    launch_id = testops_obj.create_launch(parsed_args.launch_name)
    testops_obj.upload_launch(parsed_args.reports_path, launch_id)

    allure_endpoint = os.environ.get('ALLURE_ENDPOINT')
    LOGGER.info('Test run was successfully pushed to {}/launch/{}'
                .format(allure_endpoint, launch_id))
    return 0


def get_available_actions() -> Dict:
    actions = {
        'send': send_to_testops
    }
    return actions
