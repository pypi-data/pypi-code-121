import sys
import os
import pickle
import pathlib
import shutil
import logging

import pylogconf.core
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch, get_free_args

from pydmt.configs import ConfigSudo, ConfigFlow, ConfigOutput, ConfigTarget, ConfigLogging
from pydmt.core.pydmt import PyDMT
from pydmt.static import APP_NAME, VERSION_STR, DESCRIPTION, LOGGER_NAME
from pydmt.utils.subprocess import check_call

from pydmt.features.sphinx import FeatureSphinx
from pydmt.features.mako import FeatureMako
from pydmt.features.yaml import FeatureYaml
from pydmt.features.apt import FeatureApt
from pydmt.features.npm import FeatureNpm
from pydmt.features.venv import FeatureVenv
from pydmt.features.reqs import FeatureReqs
from pydmt.features.make import FeatureMake


def add_all_features(p):
    f = FeatureApt()
    f.setup(p)
    f = FeatureNpm()
    f.setup(p)
    if ConfigTarget.dev:
        f = FeatureVenv()
        f.setup(p)
        f = FeatureMako()
        f.setup(p)
        f = FeatureSphinx()
        f.setup(p)
    else:
        f = FeatureReqs()
        f.setup(p)
    f = FeatureMake()
    f.setup(p)
    f = FeatureYaml()
    f.setup(p)


def add_to_path():
    """
    This adds to PYTHONPATH various paths we need
    If you disable this then templates would not be able to find things like 'config/python.py'
    """
    add_import_of_cwd = True
    add_import_of_home = True
    add_import_of_shared = True
    if add_import_of_shared:
        folder = "/etc/pydmt"
        if folder not in sys.path:
            sys.path.insert(0, folder)
    if add_import_of_home:
        folder = os.path.join(str(pathlib.Path.home()), ".config/pydmt")
        if folder not in sys.path:
            sys.path.insert(0, folder)
    if add_import_of_cwd:
        if "" not in sys.path:
            sys.path.insert(0, "")


@register_endpoint(
    description="Build the project",
    configs=[
        ConfigSudo,
        ConfigFlow,
        ConfigOutput,
        ConfigTarget,
        ConfigLogging,
    ],
)
def build():
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    add_all_features(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    description="Build python virtual environment",
    configs=[
        ConfigSudo,
        ConfigFlow,
        ConfigOutput,
        ConfigLogging,
    ],
)
def build_venv():
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    f = FeatureVenv()
    f.setup(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    description="Install python prerequisites",
    configs=[
        ConfigSudo,
        ConfigFlow,
        ConfigOutput,
        ConfigLogging,
    ],
)
def build_reqs():
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    f = FeatureReqs()
    f.setup(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    description="Build tools",
    configs=[
        ConfigSudo,
        ConfigFlow,
        ConfigOutput,
        ConfigLogging,
    ],
)
def build_tools():
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    f = FeatureApt()
    f.setup(p)
    f = FeatureNpm()
    f.setup(p)

    stats = p.build_all()
    sys.exit(stats.get_os_error_code())


@register_endpoint(
    description="Clean all generated files",
    configs=[
        ConfigLogging,
    ],
)
def clean() -> None:
    add_to_path()

    pylogconf.core.setup()
    p = PyDMT()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    add_all_features(p)

    shutil.rmtree(".pydmt")
    p.clean_all()


@register_endpoint(
    description="Clean all files and pydmt cache",
    configs=[
        ConfigLogging,
    ],
)
def clean_hard() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(ConfigLogging.loglevel)

    shutil.rmtree(".pydmt")
    check_call(["git", "clean", "-qffxd"])


@register_endpoint(
    description="print a pickle file for debug purposes",
    configs=[
    ],
    allow_free_args=True,
)
def print_pickle() -> None:
    for filename in get_free_args():
        with open(filename, "rb") as file_handle:
            print(f"{filename}")
            for x, y in pickle.load(file_handle).items():
                print(x, y)


@register_main(
    app_name=APP_NAME,
    version=VERSION_STR,
    main_description=DESCRIPTION,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
