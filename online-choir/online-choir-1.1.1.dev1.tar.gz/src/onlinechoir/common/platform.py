import os
import platform
from pathlib import Path


def get_windows_app_dir():
    return Path(os.environ['APPDATA'])


def get_config_folder() -> Path:
    platform_name = platform.system()
    if platform_name == "Darwin":
        folder = Path.home() / "Library" / "Preferences" / "Online Choir"
    elif platform_name == "Windows":
        folder = get_windows_app_dir() / "Online Choir"
    elif platform_name == "Linux":
        folder = Path.home() / ".online-choir"
    else:  # unknown
        return Path(__file__).parent.resolve().parent
    folder.mkdir(exist_ok=True)
    return folder


def get_log_folder() -> Path:
    platform_name = platform.system()
    if platform_name == "Darwin":
        folder = Path.home() / "Library" / "Logs" / "Online Choir"
    elif platform_name == "Windows":
        folder = get_windows_app_dir() / "Online Choir"
    elif platform_name == "Linux":
        folder = Path.home() / ".online-choir"
    else:  # unknown
        return Path(__file__).parent.resolve().parent
    folder.mkdir(exist_ok=True)
    return folder
