# -*- coding: utf-8 -*-
from re import match
from subprocess import check_call
from subprocess import check_output
from urllib.parse import urlparse


def public_git_url(remote):
    if match(r"^\w+://", remote):
        urlstr = remote
    else:
        urlstr = "ssh://" + remote
    url = urlparse(urlstr)
    path = url.path
    m = match(r".*:(\w+)$", url.netloc)
    if m:
        path = "/" + m[1] + path
    return f"https://{url.hostname}{path}"


def get_tuxsuite_remote():
    cmd = ["git", "config", "--get", "--default", "origin", "tuxsuite.remote"]
    return check_output(cmd, text=True).strip()


def get_remote_url(remote):
    cmd = ["git", "remote", "get-url", remote]
    return check_output(cmd, text=True).strip()


def get_head():
    return check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def push_head(remote, sha1):
    check_call(["git", "push", remote, f"HEAD:refs/tuxsuite/{sha1}"])


def get_git_head():
    """
    Helper function to support the "build HEAD" use case.

    Operates on the remote named in `git config tuxsuite.remote`, or "origin"
    if that is unset. The current HEAD is pushed to remote at
    refs/tuxsuite/${SHA1}, to make it available in the public repository.

    Returns a tuple containing (in this order) the public git repository URL
    calculated from the remote URL, and the SHA1 of HEAD.

    """
    remote = get_tuxsuite_remote()
    remoteurl = get_remote_url(remote)
    git_repo = public_git_url(remoteurl)
    sha1 = get_head()
    push_head(remote, sha1)
    return (git_repo, sha1)
