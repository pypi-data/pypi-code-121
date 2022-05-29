import os
from pathlib import Path

USER_HOME_PATH = Path.home()
PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))
RESOURCES_FOLDER = os.path.join(PROJECT_FOLDER, 'resources')
ICONS_FOLDER = os.path.join(RESOURCES_FOLDER, 'icons')


def get_icon(icon_name):
    """
    Returns the path of an icon

    Parameters
    ----------
    icon_name : str
        Name of the icon

    Returns
    -------
    str
        Path of the icon

    Examples
    --------
    >>> get_icon('icon.png')
    '/home/user/Documents/Projects/project/resources/icons/icon.png'
    """
    icon = os.path.join(ICONS_FOLDER, icon_name)
    if not file_exists(icon):
        icon = False

    return icon


def file_exists(file):
    """
    Checks if a file exists

    Returns
    -------
    bool
        True if the file exists, False otherwise

    Examples
    --------
    >>> file_exists('/home/user/Documents/Projects/project/resources/icons/icon.png')
    True
    >>> file_exists('/home/user/Documents/Projects/project/resources/icons/icon.png.png')
    False
    """
    return os.path.exists(file)


LOGO = get_icon("GitHub_Manager.png")
