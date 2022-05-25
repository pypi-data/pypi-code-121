import os
import json
import shutil
import tarfile
import nbformat
import jupytext
from os import devnull
from zipfile import ZipFile
from nbformat.notebooknode import NotebookNode
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from .notebook import tag_code_cells
from .config import Config


@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(devnull, "w") as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)


def read_notebook(path: str) -> NotebookNode:
    """Reads a notebook found in the given path and returns a serialized version.
    Args:
        path (str): Path of the notebook file to read.
    Returns:
        NotebookNode: Representation of the notebook following nbformat convention.
    """
    return nbformat.read(path, as_version=nbformat.NO_CONVERT)


def tag_notebook(path) -> None:
    """Adds 'graded' tag to all code cells of a notebook.

    Args:
        path (str): Path to the notebook.
    """
    nb = read_notebook(path)
    nb = tag_code_cells(nb)
    jupytext.write(nb, path)


def extract_tar(file_path: str, destination: str, post_cleanup: bool = True) -> None:
    """Extracts a tar file unto the desired destination.

    Args:
        file_path (str): Path to tar file.
        destination (str): Path where to save uncompressed files.
        post_cleanup (bool, optional): If true, deletes the compressed tar file. Defaults to True.
    """
    with tarfile.open(file_path, "r") as my_tar:
        my_tar.extractall(destination)

    if post_cleanup and os.path.exists(file_path):
        os.remove(file_path)


def extract_zip(file_path, destination, post_cleanup: bool = True) -> None:
    """Extracts a zip file unto the desired destination.

    Args:
        file_path (str): Path to zip file.
        destination (str): Path where to save uncompressed files.
        post_cleanup (bool, optional): If true, deletes the compressed zip file. Defaults to True.
    """
    with ZipFile(file_path, "r") as zip:
        zip.extractall(destination)

    if post_cleanup and os.path.exists(file_path):
        os.remove(file_path)


def send_feedback(
    score: float,
    msg: str,
    feedback_path: str = "/shared/feedback.json",
    err: bool = False,
) -> None:
    """Sends feedback to the learner.
    Args:
        score (float): Grading score to show on Coursera for the assignment.
        msg (str): Message providing additional feedback.
        feedback_path (str): Path where the json feedback will be saved. Defaults to /shared/feedback.json
        err (bool, optional): True if there was an error while grading. Defaults to False.
    """

    post = {"fractionalScore": score, "feedback": msg}
    print(json.dumps(post))

    with open(feedback_path, "w") as outfile:
        json.dump(post, outfile)

    if err:
        exit(1)

    exit(0)


def copy_submission_to_workdir(
    dir_origin: str = "/shared/submission/",
    dir_destination: str = "./submission/",
    file_name: str = "submission.ipynb",
) -> None:
    """Copies submission file from bind mount directory into working directory.
    Args:
        dir_origin (str): Origin directory.
        dir_destination (str): Target directory.
        file_name (str): Name of the file.
    """

    file_initial_path = os.path.join(dir_origin, file_name)
    file_final_path = os.path.join(dir_destination, file_name)

    shutil.copyfile(file_initial_path, file_final_path)


def update_grader_version() -> str:
    """Updates the grader version by 1 unit.

    Returns:
        str: New version of the grader.
    """
    with open("./.conf", "r") as f:
        lines = f.readlines()

    new_lines = []
    for l in lines:
        if ("GRADER_VERSION" in l) and (not "TAG_ID" in l):
            _, v = l.split("=")
            num_v = int(v)
            new_v = num_v + 1
            new_l = f"GRADER_VERSION={new_v}\n"
            new_lines.append(new_l)
            continue
        new_lines.append(l)

    with open("./.conf", "w") as f:
        f.writelines(new_lines)

    return str(new_v)


def update_notebook_version(path: str, version: str) -> None:
    """Updates notebook version to match the latest version of the grader.

    Args:
        path (str): Path to the notebook.
        version (str): Latest version of the grader to update the notebook to.
    """
    nb = read_notebook(path)
    metadata = nb.get("metadata")
    metadata.update({"dlai_version": version})
    nb["metadata"] = metadata
    jupytext.write(nb, path)


def update_grader_and_notebook_version() -> None:
    """Updates the notebook and the grader at the same time."""
    latest_version = update_grader_version()
    update_notebook_version("./mount/submission.ipynb", latest_version)
