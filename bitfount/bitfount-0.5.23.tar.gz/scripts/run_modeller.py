#!/usr/bin/env python
"""Script to run a modeller that sends tasks off to Pods."""
import logging
from os import PathLike
from pathlib import Path
from typing import Union

import fire

from bitfount.runners.modeller_runner import (
    DEFAULT_MODEL_OUT,
    run_modeller,
    setup_modeller_from_config_file,
)
from bitfount.runners.utils import setup_loggers

loggers = setup_loggers([logging.getLogger("bitfount")])


def run(
    path_to_config_yaml: Union[str, PathLike], model_out: Path = DEFAULT_MODEL_OUT
) -> None:
    """Runs a modeller from a config file."""
    modeller, pod_identifiers = setup_modeller_from_config_file(path_to_config_yaml)
    run_modeller(modeller, pod_identifiers, model_out)


def main() -> None:
    """Script entry point."""
    fire.Fire(run)


if __name__ == "__main__":
    main()
