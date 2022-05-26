from contextlib import contextmanager
from typing import Optional

from sym.shared.cli.helpers.config.base import ConfigBase
from sym.shared.cli.tests.helpers.sandbox import Sandbox as SharedSandbox

from sym.flow.cli.helpers.config import Config


class Sandbox(SharedSandbox):
    def reset_config(self):
        ConfigBase.reset()
        Config.reset()

    @contextmanager
    def setup(self, set_org: Optional[bool] = True, set_client: Optional[bool] = True):
        with self.push_xdg_config_home():
            with self.push_exec_path():
                yield
