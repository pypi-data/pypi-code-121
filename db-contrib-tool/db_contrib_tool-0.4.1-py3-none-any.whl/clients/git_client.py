"""Client for working with git."""
import subprocess
from typing import List, NamedTuple, Optional

import structlog

LOGGER = structlog.get_logger(__name__)

DEFAULT_ENCODING = "utf-8"


class GitResult(NamedTuple):
    """
    Results from running a git command.

    * return_code: Exit code of the run command.
    * output: Stdout of the run command.
    * error: Stderr of the run command.
    """

    return_code: int
    output: str
    error: str


class GitClient:
    """A client for interacting with git."""

    def merge_base(self, remote: str, branch: str) -> GitResult:
        """
        Run the merge-base command.

        :param remote: Remote repository to run against.
        :param branch: branch to pass to merge-base.
        :return: The results of running the command.
        """
        args = ["git", "merge-base", remote, branch]
        return self._run_command(args)

    def rev_parse(self, commit: str, abbrev_ref: bool = False, verify: bool = False) -> GitResult:
        """
        Run the rev-parse command.

        :param commit: Commit to run against
        :param abbrev_ref: Include the --abbrev-ref flag.
        :param verify: Include the --verify flag.
        :return: The results of running the command.
        """
        args = ["git", "rev-parse"]

        if abbrev_ref:
            args.append("--abbrev-ref")

        if verify:
            args.append("--verify")

        args.append(commit)
        return self._run_command(args)

    def rev_list(self, commit: str, number: Optional[int]) -> GitResult:
        """
        Run the rev-list command.

        :param commit: Commit to run against.
        :param number: The number of commits to output.
        :return: The results of running the command.
        """
        args = ["git", "rev-list"]

        if number:
            args.append(f"-{number}")

        args.append(commit)
        return self._run_command(args)

    @staticmethod
    def _run_command(args: List[str]) -> GitResult:
        """
        Run the given command and return the results.

        :param args: Command with arguments to run.
        :return: The results of running the command.
        """
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        output = result.stdout.decode(DEFAULT_ENCODING).strip()
        error = result.stderr.decode(DEFAULT_ENCODING).strip()
        LOGGER.debug("Git command results", cmd=args, output=output, error=error)
        return GitResult(
            return_code=result.returncode,
            output=output,
            error=error,
        )
