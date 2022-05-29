import os
from typing import Tuple, Type

from pyappconf import BaseConfig
from tests.config import ENV_PATH, TOML_PATH
from tests.fixtures.model import get_model_object, model_classes


def test_override_from_env(model_classes: Tuple[Type[BaseConfig], Type[BaseConfig]]):
    MyConfig, SubConfig = model_classes
    os.environ["MYAPP_STRING"] = "abc"
    os.environ["MYAPP_INT_TUPLE"] = "[4, 5, 6]"

    model_object = get_model_object(string="abc", int_tuple=(4, 5, 6))

    loaded_object = MyConfig.parse_toml(TOML_PATH)

    del os.environ["MYAPP_STRING"]
    del os.environ["MYAPP_INT_TUPLE"]
    assert model_object == loaded_object


def test_override_from_dotenv(model_classes: Tuple[Type[BaseConfig], Type[BaseConfig]]):
    MyConfig, SubConfig = model_classes
    ENV_PATH.write_text(
        """
MYAPP_STRING=abc
MYAPP_INT_TUPLE="[4, 5, 6]"
    """
    )

    model_object = get_model_object(string="abc", int_tuple=(4, 5, 6))

    loaded_object = MyConfig.parse_toml(TOML_PATH)

    os.remove(ENV_PATH)
    assert model_object == loaded_object
