from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, Path(__file__).parents[2].as_posix())

from mypythontools.config import MyProperty, Config

if __name__ == "__main__":

    class SimpleConfig(Config):
        def __init__(self) -> None:
            self.simple_sub_config = self.SimpleSubConfig()

        class SimpleSubConfig(Config):
            @MyProperty
            def none_arg() -> None | dict:
                return {}

            @MyProperty
            def bool_arg() -> bool:
                """This should be in CLI help."""
                return False

            @MyProperty
            def int_arg() -> int:
                """This should be in CLI help."""
                return 123

            @MyProperty
            def float_arg() -> float:
                return 123

            @MyProperty
            def str_arg() -> str:
                return "123"

            @MyProperty
            def list_arg() -> list:
                return []

            @MyProperty
            def dict_arg() -> dict:
                return {}

        @MyProperty
        def on_root() -> dict:
            """jes"""
            return {}

    config = SimpleConfig()

    config.with_argparse("How it works.")

    for i, j in config.get_dict().items():
        if "666" in str(j) or j is True or j is None:
            print(i, j, str(type(j)))
