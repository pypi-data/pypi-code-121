import os
import importlib

import pydmt.helpers.project


def get_github_username():
    mod = importlib.import_module("user.personal")
    if hasattr(mod, "github_username"):
        return getattr(mod, "github_username")
    return os.getlogin()


def get_launchpad_username():
    mod = importlib.import_module("user.personal")
    if hasattr(mod, "launchpad_username"):
        return getattr(mod, "launchpad_username")
    return os.getlogin()


def get_website():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"https://{github_username}.github.io/{name}"


def get_website_source():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"https://github.com/{github_username}/{name}"


def get_website_git():
    github_username = get_github_username()
    name = pydmt.helpers.project.get_name()
    return f"git://github.com/{github_username}/{name}.git"


def get_website_ppa():
    launchpad_username = get_github_username()
    return f"https://launchpanet/~{launchpad_username}/+archive/ubuntu/ppa"
