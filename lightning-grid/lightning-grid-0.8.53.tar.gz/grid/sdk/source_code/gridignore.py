from copy import copy
from pathlib import Path
from typing import Set
import click


def generate(src: Path) -> Set[str]:
    """
    Generates list of glob strings to ignore. These need to be parsed to identify
    which files are actually ignored.

    Parameters
    ----------
    src: Path
        Path to location where to generate ignore list from.

    Returns
    -------
    Set[str]
        Glob strings to parse
    """
    # fallback files in case we can't find .gridignore
    fallback_ignore_files = {".dockerignore", ".gitignore"}

    # never include these paths in the package
    excluded_paths = {".git"}

    # if it is a file, then just read from it and return lines
    if src.is_file():
        return _read_and_filter_gridignore(src)

    # ignores all paths from excluded paths by default
    ignore_globs = {f"{p}/" for p in excluded_paths}

    # look first for `.gridignore` files
    # Nested handling does not work anyway atm. We will concentrate to make local .gridignore file work first.
    # Previous solution that added relative paths to ignore patterns would not work as intended.
    # E.g. if in dir nested/ there's .gridignore with rule *.pyc it would ignore just files in nested/*.pyc and not in all sub-directories
    # Because .gridignore handling is somewhat complicated and non-trivial I suggest to just focus on level-0 .gridignore (non-nested)
    if (src / ".gridignore").exists():
        ignore_globs.update(_read_and_filter_gridignore(src / ".gridignore"))

    nested_gridignores = set(
        gridignore_file for gridignore_file in src.rglob(".gridignore") if gridignore_file != src / ".gridignore"
    )
    if nested_gridignores:
        click.echo(
            "We've found other .gridignore files in nested directories. Please note that currently nested .gridignore files are not supported and ignore file has to be in root directory."
        )

    # if found .gridignore, return it
    if len(ignore_globs) > len(excluded_paths):
        return ignore_globs

    # if not found, look everything else -- combine all fallback_ignore_files into one
    # This is a mess atm. We do not handle all cases of .gitinogre correctly anyway, should we actually do this?
    for path in src.glob('*'):
        if path.name in excluded_paths:
            continue
        if path.is_file():
            if path.name in fallback_ignore_files:
                filtered = _read_and_filter_gridignore(path)
                relative_dir = path.relative_to(src).parents[0]
                relative_globs = [str(relative_dir / glob) for glob in filtered]
                ignore_globs.update(relative_globs)

    return ignore_globs


def _read_and_filter_gridignore(path: Path) -> Set[str]:
    """
    Reads ignore file and filters empty lines.
    Atm we support a subset of behaviour described in https://git-scm.com/docs/gitignore

    Parameters
    ----------
    path: Path
        Path to .gridignore file or equivalent.

    Returns
    -------
    Set[str]
        Set of unique ignore pattern lines.
    """

    with path.open() as f:
        # Remove excess whitespaces and comments
        strip_lines = [ln.strip() for ln in f.readlines()]
        return {ln for ln in strip_lines if ln != "" and ln is not None and not ln.startswith("#")}
