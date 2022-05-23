import os


def get_config_dir() -> str:
    """
    Gets the directory in which to store app configuration. Based on
    code from https://stackoverflow.com/a/3250952.

    On Windows, %APPDATA%\\
    On Linux, $XDG_CONFIG_HOME/

    If the relevant environment variable for the platform is not set,
    defaults to ~/.config/

    :return:    The directory string.
    """
    # Get the system app configuration standard location
    if 'APPDATA' in os.environ:
        return os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        return os.environ['XDG_CONFIG_HOME']
    else:
        return os.path.join(os.environ['HOME'], '.config')
