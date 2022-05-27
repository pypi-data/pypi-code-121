"""Install Freesurfer license.txt file where algorithm expects it.
"""

import json
import logging
import os
import re
import shutil
from glob import glob
from pathlib import Path

from flywheel_gear_toolkit.hpc import singularity
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

log = logging.getLogger(__name__)


def check_subjects_dir_from_zip_file_path(writable_dir: Path):
    """Regardless of prior results, set the proper files in the FS subjects_dir.
    Args:
        writable_dir (Path)
    """
    paths = list(Path(writable_dir, "input/fs-subjects-dir").glob("*"))
    log.info("Using provided Freesurfer subject file %s", str(paths[0]))
    unzip_dir = writable_dir / "unzip-fs-subjects-dir"
    unzip_dir.mkdir(parents=True)
    unzip_archive(paths[0], unzip_dir)
    for a_subject in unzip_dir.glob("*/*"):
        if Path(os.environ["SUBJECTS_DIR"], a_subject.name).exists():
            log.info("Found %s but using existing", a_subject.name)
        else:
            log.info("Found %s", a_subject.name)
            a_subject.rename(Path(os.environ["SUBJECTS_DIR"], a_subject.name))


def fetch_previous_results_zip_file(
    writable_dir: Path,
    output_dir: Path,
    destination_id: str,
    prior_results_dir: Path = None,
):
    """Specifically useful for prior fMRIPrep results, but may work for other
    gears with partial analysis completion.
    Args:
        writable_dir (Path): may be /var/tmp or a user-specified directory, where Singularity
                will be able to write any number of files.
        output_dir: directory for analyzed files
        destination_id (str):
        prior_results_dir: if the manifest contains an option to resume an analysis using
            a previously analyzed zip file, the path should be specified in the config.json
            as an input file."""
    if prior_results_dir:
        paths = list(Path(prior_results_dir / "*").glob("*"))
        log.info("Using provided previous results file %s", str(paths[0]))
        unzip_dir = writable_dir / "unzip-previous-results"
        unzip_dir.mkdir(parents=True)
        unzip_archive(paths[0], unzip_dir)
        for a_dir in unzip_dir.glob("*/*"):
            log.info("Found %s", a_dir.name)
            output_analysis_id_dir = output_dir / destination_id
            a_dir.rename(output_analysis_id_dir / a_dir.name)
    else:
        log.error(
            "Invoked fetch_previous_results_zip_file, but no prior_results_dir provided"
        )


def set_FS_templates(orig_subject_dir: Path):
    """Set the template files for FreeSurfer"""
    for template in ("fsaverage", "fsaverage5", "fsaverage6"):
        singularity.mount_file(orig_subject_dir, os.environ["SUBJECTS_DIR"], template)


def set_templateflow_dir(writable_dir: Path):
    """Templateflow is already downloaded for fMRIPrep, but the pointers must be implemented
    so that the templates are not (attempted to be) re-downloaded."""
    # TemplateFlow seems to be baked in to the container since 2021-10-07 16:25:12 so this is not needed...actually, it is for now...
    templateflow_dir = writable_dir / "templateflow"
    templateflow_dir.mkdir()
    os.environ["SINGULARITYENV_TEMPLATEFLOW_HOME"] = str(templateflow_dir)
    os.environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir)
    orig = Path("/home/fmriprep/.cache/templateflow/")
    # Fill writable templateflow directory with existing templates so they don't have to be downloaded
    templates = list(orig.glob("*"))
    for tt in templates:
        # (templateflow_dir / tt.name).symlink_to(tt)
        shutil.copytree(tt, templateflow_dir / tt.name)


def setup_freesurfer_for_singularity(writable_dir: Path):
    """Overarching method to set, link, and unzip FreeSurfer-associated files.
    Args:
        writable_dir (Path): may be /var/tmp or a user-specified directory, where Singularity
                will be able to write any number of files.
    """
    new_subj_dir = Path(writable_dir, "freesurfer/subjects")
    os.environ["SUBJECTS_DIR"] = str(new_subj_dir)
    set_FS_templates(Path(os.environ["SUBJECTS_DIR"]))
    check_subjects_dir_from_zip_file_path(writable_dir, os.environ["SUBJECTS_DIR"])
