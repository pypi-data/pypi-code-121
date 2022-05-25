# Author: Snow Yang
# Date  : 2022/03/28

"""Mxos Program abstraction layer."""
import logging

from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from mdev.project.exceptions import ProgramNotFound, ExistingProgram, MxosOSNotFound
from mdev.project._internal.project_data import (
    MxosProgramFiles,
    MxosOS,
    MXOS_OS_REFERENCE_FILE_NAME,
    MXOS_OS_DIR_NAME,
)

logger = logging.getLogger(__name__)


class MxosProgram:
    """Represents an Mxos program.

    An `MxosProgram` consists of:
        * A copy of, or reference to, `MxosOS`
        * A set of `MxosProgramFiles`
        * A collection of references to external libraries, defined in .component files located in the program source tree
    """

    def __init__(self, program_files: MxosProgramFiles, mxos_os: MxosOS) -> None:
        """Initialise the program attributes.

        Args:
            program_files: Object holding paths to a set of files that define an Mxos program.
            mxos_os: An instance of `MxosOS` holding paths to locations in the local copy of the Mxos OS source.
        """
        self.files = program_files
        self.root = self.files.mxos_os_ref.parent
        self.mxos_os = mxos_os

    @classmethod
    def from_new(cls, dir_path: Path) -> "MxosProgram":
        """Create an MxosProgram from an empty directory.

        Creates the directory if it doesn't exist.

        Args:
            dir_path: Directory in which to create the program.

        Raises:
            ExistingProgram: An existing program was found in the path.
        """
        if _tree_contains_program(dir_path):
            raise ExistingProgram(
                f"An existing MXOS program was found in the directory tree {dir_path}. It is not possible to nest Mxos "
                "programs. Please ensure there is no mxos.component file in the cwd hierarchy."
            )

        logger.info(f"Creating MXOS program at path '{dir_path.resolve()}'")
        dir_path.mkdir(exist_ok=True)
        program_files = MxosProgramFiles.from_new(dir_path)
        logger.info(f"Creating git repository for the MXOS program '{dir_path}'")
        mxos_os = MxosOS.from_new(dir_path / MXOS_OS_DIR_NAME)
        return cls(program_files, mxos_os)

    @classmethod
    def from_existing(
        cls, dir_path: Path, build_subdir: Path, mxos_os_path: Path = None, check_mxos_os: bool = True,
    ) -> "MxosProgram":
        """Create an MxosProgram from an existing program directory.

        Args:
            dir_path: Directory containing an Mxos program.
            build_subdir: The subdirectory for the CMake build tree.
            mxos_os_path: Directory containing Mxos OS.
            check_mxos_os: If True causes an exception to be raised if the Mxos OS source directory does not
                           exist.

        Raises:
            ProgramNotFound: An existing program was not found in the path.
        """
        if mxos_os_path is None:
            program_root = _find_program_root(dir_path)
            mxos_os_path = program_root / MXOS_OS_DIR_NAME
        else:
            program_root = dir_path

        logger.info(f"Found existing Mxos program at path '{program_root}'")
        program = MxosProgramFiles.from_existing(program_root, build_subdir)

        try:
            mxos_os = MxosOS.from_existing(mxos_os_path, check_mxos_os)
        except ValueError as mxos_os_err:
            raise MxosOSNotFound(
                f"Mxos OS was not found due to the following error: {mxos_os_err}"
                "\nYou may need to resolve the mxos.component reference. You can do this by performing a `deploy`."
            )

        return cls(program, mxos_os)


def parse_url(name_or_url: str) -> Dict[str, str]:
    """Create a valid github/armmxos url from a program name.

    Args:
        url: The URL, or a program name to turn into an URL.

    Returns:
        Dictionary containing the remote url and the destination path for the clone.
    """
    url_obj = urlparse(name_or_url)
    if url_obj.hostname:
        url = url_obj.geturl()
    elif ":" in name_or_url.split("/", maxsplit=1)[0]:
        # If non-standard and no slashes before first colon, git will recognize as scp ssh syntax
        url = name_or_url
    else:
        url = f"https://code.aliyun.com/mxos/{url_obj.path}.git"
    # We need to create a valid directory name from the url path section.
    dist_path = url_obj.path.rsplit("/", maxsplit=1)[-1].replace("/", "")
    if dist_path.endswith('.git'):
        dist_path = dist_path[:-len('.git')]
    return {"url": url, "dst_path": dist_path}


def _tree_contains_program(path: Path) -> bool:
    """Check if the current path or its ancestors contain an mxos.component file.

    Args:
        path: The starting path for the search. The search walks up the tree from this path.

    Returns:
        `True` if an mxos.component file is located between `path` and filesystem root.
        `False` if no mxos.component file was found.
    """
    try:
        _find_program_root(path)
        return True
    except ProgramNotFound:
        return False


def _find_program_root(cwd: Path) -> Path:
    """Walk up the directory tree, looking for an mxos.component file.

    Programs contain an mxos.component file at the root of the source tree.

    Args:
        cwd: The directory path to search for a program.

    Raises:
        ProgramNotFound: No mxos.component file found in the path.

    Returns:
        Path containing the mxos.component file.
    """
    potential_root = cwd.absolute().resolve()
    while str(potential_root) != str(potential_root.anchor):
        logger.debug(f"Searching for mxos.component file at path {potential_root}")
        root_file = potential_root / MXOS_OS_REFERENCE_FILE_NAME
        if root_file.exists() and root_file.is_file():
            logger.debug(f"mxos.component file found at {potential_root}")
            return potential_root

        potential_root = potential_root.parent

    logger.debug("No mxos.component file found.")
    raise ProgramNotFound(
        f"No program found from {cwd.resolve()} to {cwd.resolve().anchor}. Please set the directory to a program "
        "directory containing an mxos.component file. You can also set the directory to a program subdirectory if there "
        "is an mxos.component file at the root of your program's directory tree."
    )
