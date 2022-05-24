""" library mfire

Météo-France's Instrument for REporting

"""

import os
import re
import argparse

from mfire.settings import Settings, RULES_NAMES, get_logger
from mfire.utils.date import Datetime


def _get_version(version_filename: str) -> str:
    """Retrieves and checks version string from VERSION file

    Args:
        version_filename (str): File containing the version string

    Returns:
        str: Version string
    """
    with open(version_filename, "r") as fp:
        version_lines = fp.readlines()
        if len(version_lines) != 1:
            raise RuntimeError("VERSION file is malformed")
        version = version_lines[0]
        version_pattern = re.compile(r"^(\d+).(\d+)(rc\d+|.dev\d+|.post\d+)?$")
        if not version_pattern.match(version):
            raise RuntimeError("VERSION string is malformed")
        return version


_VERSION_FILENAME = os.path.join(os.path.dirname(__file__), "VERSION")
__version__ = _get_version(_VERSION_FILENAME)


class CLI:
    """Class for centralizing mfire's Command Line Interface
    """

    def __init__(self) -> None:
        self.parser = self.get_parser()

    @classmethod
    def get_parser(self):
        version_header = f"{__name__} ({__version__})"
        parser = argparse.ArgumentParser(prog=f"{version_header}")
        # version
        parser.add_argument("--version", action="version", version=version_header)
        # general not in settings
        parser.add_argument(
            "-d",
            "--draftdate",
            default=Datetime(),
            help="Drafting or launching datetime",
        )
        parser.add_argument(
            "-r",
            "--rules",
            default=RULES_NAMES[0],
            choices=RULES_NAMES,
            help="Name of the rules convention (for files selection). "
            f"This argument must belong to the following list: {RULES_NAMES}",
        )
        parser.add_argument(
            "-n",
            "--nproc",
            type=int,
            default=os.cpu_count(),
            help=f"Number of CPUs [1:{os.cpu_count()}]",
        )
        parser.add_argument(
            "-t",
            "--timeout",
            help="Maximum duration in seconds of a task. Default is 600.",
        )
        parser.add_argument(
            "-e",
            "--eccodes-definition-path",
            help="Set to the folder containing the set of definition files "
            "you want ecCodes to use instead of the default one.",
        )
        # general in settings
        parser.add_argument(
            "--altitudes-filename",
            help="NetCDF file containing Digital Elevation Model on all the grids",
        )
        parser.add_argument(
            "--alternate-max",
            type=int,
            help="Maximum number of alternates to use for a single file",
        )
        parser.add_argument("-l", "--language", help="Language of the text produced")
        # working_directory
        #   general working_dir
        parser.add_argument("-w", "--working-dir", help="Working directory.")
        #   configs files
        parser.add_argument("--config-filename", help="Path to the configuration file")
        parser.add_argument(
            "--mask-config-filename", help="Path to the masks's configuration file",
        )
        parser.add_argument(
            "--data-config-filename", help="Path to the data's configuration file",
        )
        parser.add_argument(
            "--prod-config-filename",
            help="Path to the production's configuration file",
        )
        parser.add_argument(
            "--version-config-filename", help="Path to the version's configuration file"
        )
        #   mask directory
        parser.add_argument(
            "--mask-dirname", help="Path to the masks's local storage directory",
        )
        #   data directory
        parser.add_argument(
            "--data-dirname", help="Path to the data's local storage directory",
        )
        #   output directory
        parser.add_argument(
            "--output-dirname",
            help="Path to the output production's local storage directory",
        )
        #   cache directory
        parser.add_argument(
            "--cache-dirname", help="Path to the cache's local storage directory",
        )
        parser.add_argument("--save-cache", action="store_true")
        # logging
        parser.add_argument(
            "--log-level",
            help="The logging level.",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        parser.add_argument(
            "--log-file-name", default=None, type=str, help="The logging file's name.",
        )
        parser.add_argument(
            "--log-file-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="The logging level of the given log file.",
        )
        # vortex
        parser.add_argument(
            "--vapp", help="Application's name (default is 'Promethee')"
        )
        parser.add_argument(
            "--vconf", help="Application's config name (default is 'msb')"
        )
        parser.add_argument(
            "--experiment", help="Application's name (default is 'TEST')"
        )
        return parser

    def parse_args(
        self, args: list = None, namespace: argparse.Namespace = None
    ) -> argparse.Namespace:
        # retrieving args
        res = self.parser.parse_args(args=args, namespace=namespace)

        # settings
        Settings.clean()
        #   setting the full working_directory first
        if res.working_dir is not None:
            Settings.set_full_working_dir(working_dir=res.working_dir)
        #   setting the rest
        Settings.set(**res.__dict__)

        # Settings des variables d'environements hors mfire :
        # ECCODES_DEFINITION_PATH : chemin vers les definitions d'ECCODES
        if res.eccodes_definition_path is not None:
            os.environ["ECCODES_DEFINITION_PATH"] = res.eccodes_definition_path

        # puis on renvoie les args pour ce qui n'est pas directement modifiable ici
        return res


__all__ = ["__version__", "CLI", "Settings", "get_logger"]
