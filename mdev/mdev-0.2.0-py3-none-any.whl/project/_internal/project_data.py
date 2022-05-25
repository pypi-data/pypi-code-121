# Author: Snow Yang
# Date  : 2022/03/28

"""Objects representing Mxos program and library data."""
import logging

from dataclasses import dataclass
from pathlib import Path

from mdev.project._internal.render_templates import (
    render_cmakelists_template,
    render_app_cmakelists_template,
    render_main_cpp_template,
    render_mxos_config_h_template,
    render_gitignore_template,
)

logger = logging.getLogger(__name__)

# Mxos program file names and constants.
BUILD_DIR = "build"
CMAKELISTS_FILE_NAME = "CMakeLists.txt"
MAIN_C_FILE_NAME = "main.c"
MXOS_CONFIG_H_FILE_NAME = "mxos_config.h"
MXOS_OS_REFERENCE_FILE_NAME = "mxos.component"
MXOS_OS_DIR_NAME = "mxos"

# Information written to mxos.component
MXOS_OS_REFERENCE_URL = "https://code.aliyun.com/mxos/mxos.git"
MXOS_OS_REFERENCE_ID = "master"

@dataclass
class MxosProgramFiles:
    """Files defining an MxosProgram.

    This object holds paths to the various files which define an MxosProgram.

    MxosPrograms must contain an mxos.component reference file, defining Mxos OS as a program dependency.

    Attributes:
        mxos_os_ref: Library reference file for MxosOS. All programs require this file.
        cmakelists_file: A top-level CMakeLists.txt containing build definitions for the application.
        cmake_build_dir: The CMake build tree.
    """

    mxos_os_ref: Path
    cmakelists_file: Path
    cmake_build_dir: Path

    @classmethod
    def from_new(cls, root_path: Path) -> "MxosProgramFiles":
        """Create MxosProgramFiles from a new directory.

        A "new directory" in this context means it doesn't already contain an Mxos program.

        Args:
            root_path: The directory in which to create the program data files.

        Raises:
            ValueError: A program .mxos or mxos.component file already exists at this path.
        """
        app_path = root_path / root_path.name
        app_path.mkdir(exist_ok=True)

        mxos_os_ref = root_path / MXOS_OS_REFERENCE_FILE_NAME
        cmakelists_file = root_path / CMAKELISTS_FILE_NAME
        app_cmakelists_file = app_path / CMAKELISTS_FILE_NAME
        main_c = app_path / MAIN_C_FILE_NAME
        mxos_config_h = app_path / MXOS_CONFIG_H_FILE_NAME
        gitignore = root_path / ".gitignore"
        cmake_build_dir = root_path / BUILD_DIR

        if mxos_os_ref.exists():
            raise ValueError(f"Program already exists at path {root_path}.")

        mxos_os_ref.write_text(f"{MXOS_OS_REFERENCE_URL}#{MXOS_OS_REFERENCE_ID}")
        render_cmakelists_template(cmakelists_file, root_path.stem)
        render_app_cmakelists_template(app_cmakelists_file, root_path.stem)
        render_main_cpp_template(main_c, root_path.stem)
        render_mxos_config_h_template(mxos_config_h, root_path.stem)
        render_gitignore_template(gitignore)
        return cls(
            mxos_os_ref=mxos_os_ref,
            cmakelists_file=cmakelists_file,
            cmake_build_dir=cmake_build_dir,
        )

    @classmethod
    def from_existing(cls, root_path: Path, build_subdir: Path) -> "MxosProgramFiles":
        """Create MxosProgramFiles from a directory containing an existing program.

        Args:
            root_path: The path containing the MxosProgramFiles.
            build_subdir: The subdirectory of BUILD_DIR to use for CMake build.
        """

        mxos_os_file = root_path / MXOS_OS_REFERENCE_FILE_NAME

        cmakelists_file = root_path / CMAKELISTS_FILE_NAME
        if not cmakelists_file.exists():
            logger.warning("No CMakeLists.txt found in the program root.")
        cmake_build_dir = root_path / BUILD_DIR / build_subdir

        return cls(
            mxos_os_ref=mxos_os_file,
            cmakelists_file=cmakelists_file,
            cmake_build_dir=cmake_build_dir,
        )


@dataclass
class MxosOS:
    """Metadata associated with a copy of MxosOS.

    This object holds information about MxosOS used by MxosProgram.

    Attributes:
        root: The root path of the MxosOS source tree.
    """

    root: Path

    @classmethod
    def from_existing(cls, root_path: Path, check_root_path_exists: bool = True) -> "MxosOS":
        """Create MxosOS from a directory containing an existing MxosOS installation."""

        if check_root_path_exists and not root_path.exists():
            raise ValueError("The mxos directory does not exist.")

        if root_path.exists():
            raise ValueError("This MxosOS copy does not contain a mxos.component file.")

        return cls(root=root_path)

    @classmethod
    def from_new(cls, root_path: Path) -> "MxosOS":
        """Create MxosOS from an empty or new directory."""
        return cls(root=root_path)
