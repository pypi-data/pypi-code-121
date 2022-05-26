from shlex import split
from subprocess import run as _run

from .logs import get_logger

log = get_logger(__name__)


def split_args(*args):
    return split(" ".join(args))


def run(*args, **kwargs):
    logger = kwargs.pop("logger", log)
    logger.debug(" ".join(args))
    return _run(args, **kwargs)


def cmd(*args, **kwargs):
    is_shell_command = kwargs.get("shell", False)
    if kwargs.pop("collect_args", not is_shell_command):
        args = split_args(*args)
    return run(*args, **kwargs)


def git_revision_info(**kwargs):
    """Get a descriptor of the current git revision (usually used for bundling purposes).
    This will be in the format <short-commit-hash>[-dirty]?, e.g. `ee26194-dirty`.
    """
    return cmd(
        "git describe --match=NOT-EVER-A-TAG --always --abbrev --dirty", **kwargs
    )

def git_has_changes():
    """Check if there are uncommitted changes in the current git repository."""
    res = cmd("git diff-index --quiet HEAD --")
    return res.returncode != 0