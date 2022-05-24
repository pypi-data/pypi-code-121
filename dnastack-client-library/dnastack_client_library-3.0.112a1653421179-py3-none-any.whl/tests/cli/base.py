import re

from contextlib import contextmanager

import json
import logging
import os.path
import shutil
import subprocess
from json import JSONDecodeError
from typing import Dict, Any, List, Optional

from click.testing import CliRunner, Result

from dnastack.__main__ import dnastack as cli_app
from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.environments import env, flag
from dnastack.common.logger import get_logger
from dnastack.json_path import JsonPath
from ..exam_helper import BaseTestCase, ReversibleTestCase


class CliTestCase(ReversibleTestCase, BaseTestCase):
    _runner = CliRunner(mix_stderr=False)
    _debug = flag('DNASTACK_DEBUG')
    _config_file_path = env('DNASTACK_CONFIG_FILE')
    _session_dir_path = env('DNASTACK_SESSION_DIR')
    _config_overriding_allowed = flag('E2E_CONFIG_OVERRIDING_ALLOWED')

    def __init__(self, *args, **kwargs):
        super(CliTestCase, self).__init__(*args, **kwargs)
        self._logger = get_logger(f'{type(self).__name__}', self.log_level())

    @staticmethod
    def log_level():
        return logging.DEBUG if in_global_debug_mode else logging.INFO

    def setUp(self) -> None:
        super().setUp()
        self._reset_session()
        self._temporarily_remove_existing_config()

    def tearDown(self) -> None:
        super().tearDown()
        self._reset_session()
        self._restore_existing_config()

    def show_output(self) -> bool:
        return in_global_debug_mode

    @staticmethod
    def execute(command: str):
        """ Execute a shell script via subprocess directly.

            This is for debugging only. Please use :method:`invoke` for testing.
        """
        subprocess.call(command, shell=True)

    def _invoke(self, *cli_blocks: str) -> Result:
        test_envs = {
            k: 'false' if k == 'DNASTACK_DEBUG' else os.environ[k]
            for k in os.environ
        }

        # noinspection PyTypeChecker
        return self._runner.invoke(cli_app, cli_blocks, env=test_envs)

    def invoke(self, *cli_blocks: str, bypass_error: bool = False) -> Result:
        self._logger.debug(f'INVOKE: python3 -m dnastack {" ".join(cli_blocks)}')
        result = self._invoke(*cli_blocks)
        if self.show_output():
            print()
            print(f'EXEC: {" ".join(cli_blocks)}')
            if result.stderr:
                print(f'ERROR:')
                print(self._reformat_output(result.stderr))
            if result.stdout:
                print(f'STDOUT:')
                print(self._reformat_output(result.stdout))
            print()
        if result.exception and not bypass_error:
            raise result.exception
        return result

    def expect_error_from(self, cli_blocks: List[str], error_regex: Optional[str] = None,
                          error_message: Optional[str] = None):
        result = self._invoke(*cli_blocks)

        self.assertIsNotNone(result.exception, 'The exception is not raised.')
        self.assertIsInstance(result.exception, SystemExit)

        actual_error_message = result.stdout or result.stderr

        if error_regex:
            self.assertTrue(re.search(error_regex, actual_error_message) is not None,
                            f'Unexpected error message pattern\nPattern: {error_regex}\nActual: {actual_error_message}')

        if error_message:
            self.assertEqual(actual_error_message.strip(),
                             error_message.strip(),
                             f'Unexpected error message\nExpected: {error_message}\nActual: {actual_error_message}')

    def _reformat_output(self, content) -> str:
        return '\n'.join([
            f'  | {line}' for line in content.split('\n')
        ])

    def simple_invoke(self, *cli_blocks: str):
        result = self.invoke(*cli_blocks, bypass_error=False)
        self.assertEqual(0, result.exit_code,
                         'The command "' + (' '.join(cli_blocks)) + f'" returns the exit code {result.exit_code}')
        return self.parse_json(result.output)

    @staticmethod
    def parse_json(json_string: str):
        try:
            return json.loads(json_string)
        except JSONDecodeError:
            raise ValueError(f'Unable to parse this JSON string:\n\n{json_string}')

    def _configure(self, config: Dict[str, str], debug=False):
        for k, v in config.items():
            self.invoke('config', 'set', k, v)

        if debug:
            self.execute(f'cat {self._config_file_path}')

    def _temporarily_remove_existing_config(self):
        backup_path = self._config_file_path + '.backup'
        if os.path.exists(self._config_file_path):
            self._logger.debug(f"Detected the existing configuration file {self._config_file_path}.")
            if self._config_overriding_allowed:
                self._logger.debug(f"Temporarily moving {self._config_file_path} to {backup_path}...")
                shutil.copy(self._config_file_path, backup_path)
                os.unlink(self._config_file_path)
                self._logger.debug(f"Successfully moved {self._config_file_path} to {backup_path}.")
            else:
                raise RuntimeError(f'{self._config_file_path} already exists. Please define DNASTACK_CONFIG_FILE ('
                                   f'environment variable) to a different location or E2E_CONFIG_OVERRIDING_ALLOWED ('
                                   f'environment variable) to allow the test to automatically backup the existing '
                                   f'test configuration.')

    def _restore_existing_config(self):
        backup_path = self._config_file_path + '.backup'
        if os.path.exists(backup_path):
            self._logger.debug(f"Restoring {self._config_file_path}...")
            shutil.copy(backup_path, self._config_file_path)
            os.unlink(backup_path)
            self._logger.debug(f"Successfully restored {self._config_file_path}.")

    def _reset_session(self):
        if os.path.exists(self._session_dir_path):
            self._logger.debug("Removing the test session directory...")
            self.execute(f'rm -r{"v" if self._debug else ""} {self._session_dir_path}')
            self._logger.debug("Removed the test session directory.")

    def _get_endpoint(self, id: str):
        return [
            endpoint
            for endpoint in self.simple_invoke('endpoints', 'list')
            if endpoint['id'] == id
        ][0]

    def _get_endpoint_property(self, id: str, config_property: str):
        return JsonPath.get(self._get_endpoint(id), config_property)

    def _configure_endpoint(self, id: str, props: Dict[str, Any]):
        for k, v in props.items():
            self.invoke('endpoints', 'set', id, k, str(v))

        endpoint = self._get_endpoint(id)

        for k, v in props.items():
            self.assertEqual(JsonPath.get(endpoint, k), v)
