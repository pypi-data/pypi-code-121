import importlib
import unittest
from typing import List
from unittest import mock

from click.testing import CliRunner, Result

from vgscli.vgs import cli


class CliRunnerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def invoke(self, command: List[str]) -> Result:
        return self.runner.invoke(cli, args=[*command])

    def assertExitCode(self, result: Result, exit_code: int) -> None:
        self.assertEqual(exit_code, result.exit_code, 'Unexpected exit code')

    def assertOutput(self, result: Result, output: str) -> None:
        self.assertEqual(output, result.output, 'Unexpected output')


# https://stackoverflow.com/questions/52324568
def patch(*args, **kwargs):
    target = args[0].split('.')

    for i in range(len(target), 0, -1):
        # noinspection PyBroadException
        try:
            module = importlib.import_module('.'.join(target[:i]))

            # noinspection PyShadowingNames
            patch = mock.patch(*args, **kwargs)
            patch.attribute = '.'.join(target[i:])
            patch.getter = lambda: module
            return patch
        except Exception:
            pass

    return mock.patch(*args, **kwargs)
