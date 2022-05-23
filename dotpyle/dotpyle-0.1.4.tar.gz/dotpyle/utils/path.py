from os import getenv, path
from re import search
from dotpyle.utils import constants


def get_default_path() -> str:
    """
    We need to know where to store information. If XDG_CONFIG_HOME is defined, use it.
    In any other case, it will use click.get_app_dir as default.

    Ref: https://click.palletsprojects.com/en/7.x/api/#click.get_app_dir
    """

    # TODO On MacOs get_app_dir return ~/Applications/Application Support/{NAME}
    default_config_path = getenv("XDG_CONFIG_HOME", "~/.config")

    return path.expanduser("{0}/{1}".format(default_config_path,
                                            constants.APP_NAME))


def un_expanduser(path: str) -> str:
    """ translate /home/<username>/path into ~/path"""

    home_path = getenv("HOME")
    path_from_home = search("^{0}(.+?)$".format(home_path), path)
    if path_from_home:
        return "~" + path_from_home.group(1)
    return path


def get_configuration_path() -> str:
    return path.join(get_default_path(), constants.DOTPYLE_CONFIG_FILE_NAME)


def get_local_configuration_path() -> str:
    return path.join(get_default_path(),
                     constants.DOTPYLE_LOCAL_CONFIG_FILE_NAME)


def get_dotfiles_path() -> str:
    return path.join(get_default_path(), constants.DOTFILES_FOLDER)


def get_dotpyle_name_path(name: str) -> str:
    return path.join(get_dotfiles_path(), name)


def get_dotpyle_profile_path(name: str, profile: str) -> str:
    return path.join(get_dotpyle_name_path(name), profile)


def get_repo_paths(name: str, profile: str, dotfile_path: str) -> str:
    return path.join(get_dotpyle_profile_path(name, profile), dotfile_path)


def get_link_path(root: str, dotfile_path: str) -> str:
    return path.expanduser(path.join(root, dotfile_path))


def get_source_and_link_path(name: str, profile: str, root: str,
                             dotfile_path: str) -> tuple[str, str]:
    """
    source: absolute path for name+profile inside dotpyle repo
    link_name: absolute path for name+profile on real system
    """
    return get_repo_paths(name, profile, dotfile_path), get_link_path(root, dotfile_path)


def get_dotpyle_readme_path() -> str:
    return path.join(get_default_path(), constants.README_NAME)


def get_scripts_path() -> str:
    return path.join(get_default_path(), constants.SCRIPTS_FOLDER)


def get_script_path(filename: str) -> str:
    return path.join(get_default_path(), constants.SCRIPTS_FOLDER, filename)


def get_basename(full_path: str) -> str:
    return path.basename(full_path)


if __name__ == "__main__":
    print(un_expanduser("/home/perseo/ao/aoeu/eih"))
    print(un_expanduser("/ome/perseo/ao/aoeu/eih"))
    print(un_expanduser("/usr/home/perseo/aoe"))
