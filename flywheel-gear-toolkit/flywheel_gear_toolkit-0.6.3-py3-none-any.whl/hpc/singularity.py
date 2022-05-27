import logging
import os
import shutil
import tempfile
from glob import glob
from pathlib import Path

from flywheel_gear_toolkit.context.constants import FW_HOME

log = logging.getLogger(__name__)


def check_for_singularity():
    """Determine if Singularity is enabled on the system and log it.
    Singularity auto-populates several ENV variables at runtime.
    https://sylabs.io/guides/3.7/user-guide/environment_and_metadata.html#environment-overview"""
    if "SINGULARITY_NAME" in os.environ:
        log.info("Singularity detected.")
        return True
    else:
        log.info("Singularity not detected. Using standard Docker setup.")
        return False


def check_writable_dir(writable_dir: Path):
    """
    Returns True if the input directory is writable; false otherwise.
    """
    if os.access(writable_dir, os.W_OK):
        log.info(f"{writable_dir} is writable.")
        return True
    else:
        log.info(f"{writable_dir} is NOT writable. Will check other options.")
        return False


def log_singularity_details():
    """Help debug Singularity settings, including permissions and UID."""
    log.info(f"SINGULARITY_NAME is {os.environ['SINGULARITY_NAME']}")
    log.debug(f"UID is {os.getuid()}")


def mount_file(orig_path: Path, new_path: Path, filename: str):
    """Add symlinks for writable directories."""
    if not new_path.exists():
        new_path.mkdir(parents=True)
    Path(new_path, filename).symlink_to(Path(orig_path, filename))


def mount_gear_home_to_tmp(gear_name: str, writable_dir: Path):
    """
    - Singularity auto-mounts /tmp and /var/tmp.
    - The Docker run.py script is initialized after creation of the
    Singularity container.
    - Therefore, there is no opportunity to mount /flywheel/v0 data
    or structure directly to Singularity.
    The resulting necessity is to use this method to create a
    subfolder inside the automounted /tmp directory that will
    contain the files Docker is instructed to use to run the gear.
    """
    # Create temporary place to run gear
    work_dir = tempfile.mkdtemp(prefix=gear_name, dir=writable_dir)
    new_fw_home = Path(work_dir + FW_HOME)
    new_fw_home.mkdir(parents=True)
    abs_path = Path(".").resolve()
    fw_paths = Path(FW_HOME).glob("*")

    for fw_name in fw_paths:
        # if fw_name.name == "gear_environ.json":  # always use real one, not dev
        #     mount_file(Path(FW_HOME), new_fw_home, fw_name.name)
        # else:
        Path(new_fw_home, fw_name.name).symlink_to(Path(abs_path, fw_name.name))
    os.chdir(new_fw_home)
    return new_fw_home


def start_singularity(
    gear_name: str, user_given_writable_dir: Path = "/var/tmp", debug: bool = False
):
    """
    Set up the environment for a clean Singularity run.
    Ensure there are writable directories and mount the writable directories to /flywheel/v0
    Args:
        gear_name (str): Name of the gear associated with the gear; advisable to require input from
            the user, so that multiple HPC-based runs of the same gear with the same name is avoided. Secondary
            best practice is to grab the "name" field from the manifest as a default.
        user_given_writable_dir (Path): directory to use for temporary files if /flywheel/v0 is not
            writable.
        debug (bool): Log level set for the gear.
    Returns:
        writable_dir (Path): name of the directory to be used throughout the remainder of the gear run.
    """
    # Set the typical home directory for the gear, if running in Docker

    if debug:
        log_singularity_details()

    # Favor containing the gear in normal gear locations by checking /flywheel/v0 first
    if check_writable_dir(FW_HOME):
        writable_dir = FW_HOME
    # If those directories are not writable, check the user-supplied writing location
    elif check_writable_dir(user_given_writable_dir):
        writable_dir = user_given_writable_dir

    try:
        mount_gear_home_to_tmp(gear_name, writable_dir)
        return writable_dir
    except UnboundLocalError:
        log.error(
            f"Did not find a writable directory. Checked {FW_HOME} and {user_given_writable_dir}"
        )


def unlink_gear_mounts(writable_dir: Path):
    """
    Clean up the shared environment, since pieces (like FreeSurfer) may have
    left remnants in temporary directories.
    """
    for item in glob(Path(writable_dir, "*")):
        if os.path.islink(item):
            os.unlink(item)  # don't remove anything links point to
            log.debug("unlinked {item}")
    shutil.rmtree(writable_dir)
    log.debug(f"Removed {writable_dir}")
