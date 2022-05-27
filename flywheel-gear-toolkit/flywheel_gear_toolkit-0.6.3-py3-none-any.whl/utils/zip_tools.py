"""
Module collection of zip utilities.
"""
import json
import logging
import os
import os.path as op
import re
from zipfile import ZIP_DEFLATED, ZipFile

log = logging.getLogger(__name__)


def unzip_archive(zipfile_path, output_dir, dry_run=False):
    """Unzips the content of a zip archive file to a specified location.

    Unzips the contents of `zipfile_path` relative to `output_dir`. Active if the
    `dry_run` parameter is False. Contents of the zip archive file can be viewed
    with :func:`gear_toolkit.utils.zip_tools.view_zipfile_contents`.

    Args:

        zipfile_path (str): Absolute path to zip file.
        output_dir (str): Absolute path of directory to place contents of extracted
            zipfile_path.
        dry_run (boolean, optional): If True, this does not unzip the zip file. This is
            a flag that can be utilized for debugging gear
            commands initiated but not executed.

    Examples:
            >>> unzip_all('/flywheel/v0/inputs/ZIP/file.zip', '/flywheel/v0/work/')
            >>> unzip_all('/flywheel/v0/inputs/ZIP/file.zip', '/flywheel/v0/work/', dry_run = True)
    """
    input_zip = ZipFile(zipfile_path, "r")
    log.info("Unzipping file, %s", zipfile_path)

    if not dry_run:
        input_zip.extractall(output_dir)


def get_config_from_zip(zipfile_path, search_str=r"_config\.json"):
    """Return the config as a dictionary from .json files within a zip archive file.

    This function reads a file with filename matching `search_str` from `zipfile_path`
    and returns the contents of that file as a python dictionary.

    Args:
        zipfile_path (str): Absolute path of zip file whose contents will be searched.
        search_str (regexp, optional): Regular expression string for the name of the
            file to be searched. Must be a .json file. Defaults to '_config.json'.

    Returns:
        (dict): dictionary of `search_str` file contents.

    Example:
        >>> config = get_config_from_zip('/flywheel/v0/inputs/ZIP/file.zip')
    """

    config = {}
    zf = ZipFile(zipfile_path)
    for fl in zf.filelist:
        if fl.filename[-1] != os.path.sep:  # not (fl.is_dir()):
            # if search_str in filename
            if re.search(search_str, fl.filename):
                json_str = zf.read(fl.filename).decode()
                config = json.loads(json_str)

                # This corrects for leaving the initial "config" key out
                # of previous gear versions without error
                if "config" not in config.keys():
                    config = {"config": config}

    if not config:
        log.warning("Configuration file is empty or not found.")
        return None

    return config


def zip_output(
    root_dir,
    source_dir,
    output_zip_filename,
    dry_run=False,
    exclude_files=None,
):
    """Zip an output directory.

    Zips the complete output of the gear relative `root_dir` (e.g. /flywheel/v0/work)
    and saves the output to `output_zip_path` (e.g. /flywheel/v0/output/bids.zip).

    Args:
        root_dir (str): The root directory to zip relative to.
        source_dir (str): subdirectory (of <root_dir>) to zip.
        output_zip_filename (str): Full path of the resultant output zip file.
        dry_run (boolean, optional): Boolean value that determines whether or not to
            execute a full zip compression of source_dir.
        exclude_files (list, optional): Files in <root_dir>/<source_dir> to exclude
            from the zip file. Defaults to `None`.

    Raises:
        FileNotFoundError: If `root_dir` does not exist.

    Examples:
        >>> zip_output('/flywheel/v0/work','gear_output','output.zip')
        >>> zip_output('/flywheel/v0/work','gear_output','output.zip', dry_run=True)

        .. code-block:: python

            zip_output(
                '/flywheel/v0/work','gear_output','output.zip',
                exclude_files=['sub_dir1/file1.txt','sub_dir2/file2.txt']
            )


    """

    if exclude_files:
        exclude_from_output = exclude_files
    else:
        exclude_from_output = []

    # if root_dir is not defined, set it to the working directory
    if not op.exists(root_dir):
        raise FileNotFoundError(f"The directory, {root_dir}, does not exist.")

    log.info("Zipping output file %s", output_zip_filename)
    if not dry_run:
        try:
            os.remove(output_zip_filename)
        except FileNotFoundError:
            pass

        os.chdir(root_dir)
        with ZipFile(output_zip_filename, "w", ZIP_DEFLATED) as outzip:
            for root, subdirs, files in os.walk(source_dir):
                for fl in files + subdirs:
                    fl_path = op.join(root, fl)
                    # only if the file is not to be excluded from output
                    if fl_path not in exclude_from_output:
                        outzip.write(fl_path)


def zip_info(zipfile_path):
    """
    Retrieve a list of relative file paths stored the zip archive.

    Args:
        zipfile_path (str): Absolute path of the zip file.

    Returns:
        (list): List of relative paths for all files in the zip archive.

    Example:
        >>> file_info = zip_info('/path/to/zipfile.zip')

    """

    return sorted(
        filter(
            lambda x: len(x) > 0,
            [
                x.filename if (x.filename[-1] != os.path.sep) else ""
                for x in ZipFile(zipfile_path).filelist
            ],
        )
    )
