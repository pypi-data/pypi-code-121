from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

import jijzept.config.config_command
import jijzept.config.config_command as config_command
import jijzept.config.handle_config
import jijzept.config.handle_config as handle_config

from jijzept.config.handle_config import Config

__all__ = [
    "Config",
]
