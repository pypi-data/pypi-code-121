""" Helper utility functions for validations of api in models.py"""

from tuxbake.exceptions import TuxbakeParsingError
import re


def check_instance(value: any, type: any, err_msg) -> None:
    """check the type of arguments"""
    if not isinstance(value, type):
        raise TuxbakeParsingError(err_msg)


def validate_git_repo(url):
    """Validate the git_repo api argument"""
    if not url:
        raise TuxbakeParsingError("git url not provided!!")

    check_instance(
        url,
        str,
        f"Unexpected argument for 'url', expected string: '{url}'",
    )
    if "://" in url:
        url_re = re.compile(r"^(http|git|https)://[^ ]+$")
        repo_url_max_length = 1024

        if not url_re.match(url):
            raise TuxbakeParsingError(f"Unexpected argument for git url: '{url}'")

        if len(url) > repo_url_max_length:
            raise TuxbakeParsingError(
                f"url argument '{url}' too long: '{len(url)} chars'"
            )


def validate_environment(environment):
    """
    Validate environment argument which is a dictionary.
    """
    check_instance(
        environment,
        dict,
        f"Expected a dict in environment: '{environment}'",
    )
    # TODO: check key value pair of type string
    for key, value in environment.items():
        check_instance(
            key,
            str,
            f"Unexpected argument for environment key : {key}, expected string: '{key}'",
        )
        check_instance(
            value,
            str,
            f"Unexpected argument for environment value of key : {key}, expected string: '{value}'",
        )


def validate_git_ref(git_ref):
    """Validate the git_ref api argument"""

    git_ref_re = re.compile(r"^[/\w_.-]+$")
    git_ref_max_length = 128

    check_instance(
        git_ref,
        str,
        f"Unexpected argument for git_ref, expected string: '{git_ref}'",
    )

    if not git_ref_re.match(git_ref):
        raise TuxbakeParsingError(f"Unexpected argument for git_ref: '{git_ref}'")
    if len(git_ref) > git_ref_max_length:
        raise TuxbakeParsingError(
            f"git_ref argument '{git_ref}' too long: '{len(git_ref)} chars'"
        )


def validate_git_sha(git_sha):
    """Validate the git_sha api argument"""

    git_sha_re = re.compile(r"^[0-9a-f]{40}$")

    check_instance(
        git_sha,
        str,
        f"Unexpected argument for git_sha, expected string: '{git_sha}'",
    )

    if not git_sha_re.match(git_sha):
        raise TuxbakeParsingError(
            f"Unexpected argument for git_sha: '{git_sha}'; "
            "expected 40 lowercase hexadecimal characters."
        )


def validate_container(container):

    supported_containers = [
        "ubuntu-22.04",
        "ubuntu-20.04",
        "ubuntu-18.04",
        "ubuntu-16.04",
        "centos-8",
        "debian-bullseye",
        "debian-buster",
        "debian-stretch",
        "fedora-33",
        "fedora-34",
        "opensuse-leap-15.1",
        "opensuse-leap-15.2",
    ]
    check_instance(
        container,
        str,
        f"Unexpected argument for container, expected string: '{container}'",
    )
    if container not in supported_containers:
        raise TuxbakeParsingError(
            f"Unexpected argument for container: '{container}'; "
            "container not supported or is invalid!!"
        )


def validate_local_conf(local_conf):

    check_instance(
        local_conf,
        list,
        f"Unexpected argument for local_conf, expected list: '{local_conf}'",
    )
    for conf in local_conf:
        check_instance(
            conf,
            str,
            f"Unexpected argument for local_conf data, expected string: '{conf}'",
        )


def validate_bblayers_conf(bblayers_conf):

    check_instance(
        bblayers_conf,
        list,
        f"Unexpected argument for bblayers_conf, expected list: '{bblayers_conf}'",
    )
    for bb_conf in bblayers_conf:
        check_instance(
            bb_conf,
            str,
            f"Unexpected argument for bblayers_conf data, expected string: '{bb_conf}'",
        )
