import os
import warnings
import shutil
import argparse

from yggdrasil.app_manager import AppManager, PATH_YGGDRASIL, PATH_INTERNAL
from yggdrasil.utilities.logger import logger


def seed():
    """
    Generates yggdrasil base folder template.
    If a path is defined in YGGDRASIL_ROOT environment variable, it will be created under the given path.
    If not, it will resort to a default path (under user Documents).
    Under the Yggdradil root folder, will be generated:
    - tools folder: Store base code repos
    - venvs folder: Store virtual environments for each drivers
    - settings: Store congiguration file for drivers creation
    - scripts: Store batch files for each drivers
    At runtime, this function will also create a settings.yaml template (under settings folder) and a
    ls_tools.bat file (under scripts folder), listing the drivers installed under yggdrasil
    """
    path_root = PATH_YGGDRASIL
    os.mkdir(path_root)
    os.mkdir(r'{0}\venvs'.format(path_root))
    os.mkdir(r'{0}\scripts'.format(path_root))
    os.mkdir(r'{0}\settings'.format(path_root))
    shutil.copy(
        r'{0}\data\ls_tools.txt'.format(PATH_INTERNAL),
        r'{0}\scripts\ls_tools.bat'.format(path_root)
    )
    shutil.copy(
        r'{0}\data\template_settings.yaml'.format(PATH_INTERNAL),
        r'{0}\settings\settings.yaml'.format(path_root)
    )
    if r"{0}\scripts".format(path_root) not in os.environ['Path'].split(";"):
        warnings.warn(r"Please add {0}\scripts to your Path variable for easier access to utilities".format(path_root))


def run(cmd: str, **kwargs):
    """
    Base runner for AppManager.
    :param cmd: Command to run ("make", "update" or "remove")
    :param kwargs: Depending on the command run (debug parameter for all functions, force_regen for drivers creation)
    This function gives access to the underlying runner for any command on the AppManager, in case finer control
    / more agnostic code is needed instead of the simpler functions of the module (create, remove, update)
    """
    apps = kwargs.pop("apps", None)
    debug = kwargs.get("debug")
    if debug:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")
    mger = AppManager.from_default()
    if apps == '*':
        apps = [app.name for app in mger.apps]
    elif isinstance(apps, str):
        apps = [apps]
    mger.functions[cmd](apps, **kwargs)


def create(apps, debug=False, force_regen=False):
    """
    Creates an application
    :param apps: Name of the application (as per settings file). Can accept a single app (string), a list of apps ([]),
    or all apps ("*")
    :param debug: Run in debug mode (True) or standard mode (False), affecting level of logging & drivers creation behaviour.
    False by default
    :param force_regen: Force re-creation of the drivers if it already exists or not. If False & the drivers already exists,
    creation will be skipped. If True, then drivers will be completely removed before being re-created
    """
    run("create", apps=apps, debug=debug, force_regen=force_regen)


def remove(apps, debug=False):
    """
    Removes an application
    :param apps: Name of the application (as per settings file). Can accept a single app (string), a list of apps ([]),
    or all apps ("*")
    :param debug: Run in debug mode (True) or standard mode (False), affecting level of logging & drivers creation behaviour.
    False by default
    """
    run("remove", apps=apps, debug=debug)


def show(apps):
    """
    Shows the list of applications
    :param apps: Name of the application (as per settings file). Can accept a single app (string), a list of apps ([]),
    or all apps ("*")
    """
    run("show", apps=apps)


def cmd_ygg():
    """
    Command line interface for yggdrasil.
    """
    parser = argparse.ArgumentParser(prog="yggdrasil")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # Seed function subparser
    parser_seed = subparsers.add_parser("seed", help="Seed template structure for yggdrasil")

    # Create function subparser
    parser_create = subparsers.add_parser("create", help="Create an application")
    parser_create.add_argument("-d", "--debug", action="store_true", help="Show debug log during execution")
    parser_create.add_argument("-f", "--force-regen", action="store_true", dest="force_regen", help="Forces regeneration of the app if already exists")
    parser_create.add_argument("apps", nargs='*', default='*', help="List of apps to create (all if not specified)")

    # Remove function subparser
    parser_remove = subparsers.add_parser("remove", help="Create an application")
    parser_remove.add_argument("-d", "--debug", action="store_true", help="Show debug log during execution")
    parser_remove.add_argument("apps", nargs='*', default='*', help="List of apps to remove (all if not specified)")

    # Show function subparser
    parser_show = subparsers.add_parser("show", help="Show list of existing applications")
    parser_show.add_argument("apps", default='*', nargs='*')

    args = parser.parse_args()
    if vars(args).get("cmd") == "seed":
        seed()
    else:
        run(**vars(args))
