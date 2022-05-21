"""Module with functions for 'project_utils' subpackage."""

from __future__ import annotations
from typing import Sequence, Any
import os
import sys

from typing_extensions import Literal

from mypythontools.config import Config, MyProperty
from mypythontools.misc import GLOBAL_VARS, EMOJIS, print_progress
from mypythontools.paths import PathLike
from mypythontools.types import validate_sequence

from .. import tests
from .. import venvs
from ..deploy import deploy_to_pypi
from .project_utils_functions import (
    git_commit_all,
    get_version,
    git_push,
    reformat_with_black,
    set_version,
    docs_regenerate,
)

# Lazy loaded
# from git import Repo

from mypythontools_cicd.project_paths import PROJECT_PATHS


class PipelineConfig(Config):
    """Allow to setup CICD pipeline."""

    @MyProperty
    @staticmethod
    def do_only() -> Literal[
        None,
        "prepare_venvs",
        "reformat",
        "test",
        "docs",
        "sync_requirements",
        "git_commit_all",
        "git_push",
        "deploy",
    ]:
        """Run just single function from pipeline, ignore the others.

        Type:
            Literal[
                None, "prepare_venvs", "reformat", "test", "docs", "sync_requirements", "git_commit_all",
                "git_push", "deploy"
            ]

        Default:
            None

        Reason for why to call it form here and not directly is to be able to use sys args or single command
        line entrypoint.
        """
        return None

    @MyProperty
    @staticmethod
    def prepare_venvs() -> None | list[str]:
        """Create venvs with defined versions.

        Type:
            list[str]

        Default:
            ["3.7", "3.10", "wsl-3.7", "wsl-3.10"]
        """
        return ["3.7", "3.10", "wsl-3.7", "wsl-3.10"]

    @MyProperty
    @staticmethod
    def prepare_venvs_path() -> PathLike:
        """Prepare venvs in defined path.

        Type:
            str

        Default:
            "venv"
        """
        return "venv"

    @MyProperty
    @staticmethod
    def reformat() -> bool:
        """Reformat all python files with black. Setup parameters in pyproject.toml.

        Type:
            bool

        Default:
            True.
        """
        return True

    @MyProperty
    @staticmethod
    def test() -> None | tests.TestConfig:
        """Run pytest tests.

        Type:
            bool

        Default:
            True
        """
        return tests.default_test_config

    @MyProperty
    @staticmethod
    def version() -> None | str:
        """Overwrite __version__ in __init__.py.

        Type:
            str

        Default:
            'increment'.

        Version has to be in format like '1.0.3' three digits and two dots. If 'None', nothing will happen. If
        'increment', than it will be updated by 0.0.1..
        """
        return "increment"

    @MyProperty
    @staticmethod
    def docs() -> bool:
        """Whether generate sphinx apidoc and generate rst files for documentation. Some files in docs source
        can be deleted - check `docs` docstrings for details.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def sync_requirements() -> None | Literal["infer"] | PathLike | Sequence[PathLike]:
        """Check requirements.txt and update all the libraries.

        Type:
            None | Literal["infer"] | PathLike | Sequence[PathLike]

        Default:
            None

        You can use path to requirements, list of paths or bool value. If True, then path is inferred.
        """
        return None

    @MyProperty
    @staticmethod
    def git_commit_all() -> None | str:
        """Whether take all the changes in repository and create a commit with these changes.

        Note:
            !!! Be cautious here !!!

        Type:
            None | str

        Default:
            'New commit'
        """
        return "New commit"

    @MyProperty
    @staticmethod
    def git_push() -> bool:
        """Whether push to repository.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def tag() -> str:
        """Tag. E.g 'v1.1.2'. If '__version__', get the version.

        Type:
            str

        Default:
            '__version__'
        """
        return "__version__"

    @MyProperty
    @staticmethod
    def tag_message() -> str:
        """Tag message.

        Type:
            bool

        Default:
            'New version'
        """
        return "New version"

    @MyProperty
    @staticmethod
    def deploy() -> bool:
        """Deploy to PYPI.

        `TWINE_USERNAME` and `TWINE_PASSWORD` are used for authorization.

        Type:
            bool

        Default:
            False
        """
        return False

    @MyProperty
    @staticmethod
    def allowed_branches() -> None | Sequence[str]:
        """Pipeline runs only on defined branches.

        Type:
            None | Sequence[str]

        Default:
            ["master", "main"]
        """
        return ["master", "main"]

    @MyProperty
    @staticmethod
    def verbosity() -> Literal[0, 1, 2]:
        """Pipeline runs only on defined branches.

        Type:
            Literal[0, 1, 2]

        Default:
            1
        """
        return 1


default_pipeline_config = PipelineConfig()
"""Default values for pipeline. If something changes here, it will change in all the repos. You can edit any
values in pipeline. Intellisense and help tooltip should help."""


def project_utils_pipeline(
    config: PipelineConfig = default_pipeline_config,
) -> None:
    """Run pipeline for pushing and deploying an app or a package.

    Can run tests, generate rst files for sphinx docs, push to github and deploy to pypi. All params can be
    configured not only with function params, but also from command line with params and therefore callable
    from terminal and optimal to run from IDE (for example with creating simple VS Code task).

    Some function suppose some project structure (where are the docs, where is `__init__.py` etc.).
    If you are issuing some error, try functions directly, find necessary paths in parameters
    and set paths that are necessary in paths module.

    Note:
        Beware, that by default, it creates a commit and add all the changes, not only the staged ones.

    When using sys args for boolean values, always define True or False.

    There is command line entrypoint called `mypythontools_cicd`. After mypythontools is installed, you can
    use it in terminal like::

        mypythontools_cicd --do_only reformat

    Args:
        config (PipelineConfig, optional): PipelineConfig object with CICD pipeline configuration. Just import
            default_pipeline_config and use intellisense and help tooltip with description. It is also
            possible to configure all the params with CLI args from terminal.
            Defaults to `default_pipeline_config`.

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how to use it.
        You can also use it from python... ::

            from mypythontools_cicd.project_utils import project_utils_pipeline, default_pipeline_config

            default_pipeline_config.deploy = True
            # default_pipeline_config.do_only = ""


            if __name__ == "__main__":
                # All the parameters can be overwritten via CLI args
                project_utils_pipeline(config=default_pipeline_config)

        It's also possible to use CLI and configure it via args. This example just push repo to PyPi. ::

            python path-to-project/utils/push_script.py --do_only deploy

    Another way how to run it is to use IDE. For example in VS Code you can use Tasks. Check `project_utils`
    docs for examples.
    """

    if not GLOBAL_VARS.is_tested:
        config.with_argparse()

    if config.do_only:
        do_only_value = config[config.do_only]
        config.update(
            {
                "prepare_venvs": None,
                "reformat": False,
                "test": None,
                "docs": False,
                "sync_requirements": None,
                "git_commit_all": None,
                "git_push": False,
                "deploy": False,
                "version": None,
            }
        )
        config.update({config.do_only: do_only_value})

        if config.verbosity == 1:
            config.verbosity = 0

    if config.prepare_venvs:
        venvs.prepare_venvs(
            path=config.prepare_venvs_path,
            versions=config.prepare_venvs,
        )

    verbose = True if config.verbosity == 2 else False
    progress_is_printed = config.verbosity > 0

    if config.allowed_branches:
        import git.repo
        from git.exc import InvalidGitRepositoryError

        validate_sequence(config.allowed_branches, "allowed_branches")

        try:
            branch = git.repo.Repo(PROJECT_PATHS.root.as_posix()).active_branch.name
        except InvalidGitRepositoryError:
            raise RuntimeError(
                "Loading of git project failed. Verify whether running pipeline from correct path. If "
                "checks branch with `allowed_branches', there has to be `.git` folder available."
            ) from None

        if branch not in config.allowed_branches:
            raise RuntimeError(
                "Pipeline started on branch that is not allowed."
                "If you want to use it anyway, add it to allowed_branches parameter and "
                "turn off changing version and creating tag."
            )

    # Do some checks before run pipeline so not need to rollback eventually
    if config.deploy:
        usr = os.environ.get("TWINE_USERNAME")
        pas = os.environ.get("TWINE_PASSWORD")

        if not usr or not pas:
            raise KeyError("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")

    if config.sync_requirements:
        print_progress("Syncing requirements", progress_is_printed)

        if not venvs.is_venv:
            raise RuntimeError("'sync_requirements' available only if using virtualenv.")
        my_venv = venvs.Venv(sys.prefix)
        my_venv.create()
        my_venv.sync_requirements(config.sync_requirements, verbose=verbose)

    if config.test:
        print_progress("Testing", progress_is_printed)
        tests.run_tests(config.test)

    if config.reformat:
        print_progress("Reformatting", progress_is_printed)
        reformat_with_black()

    if config.version and config.version != "None":
        print_progress("Setting version", progress_is_printed)
        original_version = get_version()
        set_version(config.version)

    try:
        if config.docs:
            print_progress("Sphinx docs generation", progress_is_printed)
            docs_regenerate(verbose=verbose)

        if config.git_commit_all:
            print_progress("Creating commit of all changes", progress_is_printed)
            git_commit_all(config.git_commit_all, verbose=verbose)

        if config.git_push:
            print_progress("Pushing to github", progress_is_printed)
            git_push(
                tag=config.tag,
                tag_message=config.tag_message,
                verbose=verbose,
            )

    except Exception as err:  # pylint: disable=broad-except
        if config.version:
            set_version(original_version)  # type: ignore

        raise RuntimeError(
            f"{3 * EMOJIS.DISAPPOINTMENT} Utils pipeline failed {3 * EMOJIS.DISAPPOINTMENT} \n\n"
            "Original version restored. Nothing was pushed to repo, you can restart pipeline."
        ) from err

    try:
        if config.deploy:
            print_progress("Deploying to PyPi", progress_is_printed)
            deploy_to_pypi(verbose=verbose)

    except Exception as err:  # pylint: disable=broad-except
        raise RuntimeError(
            f"{3 * EMOJIS.DISAPPOINTMENT} Deploy failed {3 * EMOJIS.DISAPPOINTMENT} \n\n"
            "Already pushed to repository. Deploy manually. Version already changed.",
        ) from err

    print_progress(f"{3 * EMOJIS.PARTY} Finished {3 * EMOJIS.PARTY}", True)
