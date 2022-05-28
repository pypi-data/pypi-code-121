from subprocess import check_call, CalledProcessError

import logging


def require_clean_work_tree() -> bool:
    check_call(["git", "update-index", "-q", "--ignore-submodules", "--refresh"])

    try:
        check_call(["git", "diff-files", "--quiet", "--ignore-submodules", "--"])
    except CalledProcessError:
        logging.error("You have unstaged changes.")
        return False

    try:
        check_call(["git", "diff-index", "--cached", "--quiet", "HEAD", "--ignore-submodules", "--"])
    except CalledProcessError:
        logging.error("Your index contains uncommitted changes.")
        return False

    return True
