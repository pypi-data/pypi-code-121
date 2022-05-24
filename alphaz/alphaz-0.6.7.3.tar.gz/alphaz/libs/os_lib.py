import sys, platform

SYSTEM_PLATFORM = platform.system().lower()

def is_linux():
    return SYSTEM_PLATFORM == "linux"

def is_windows():
    return SYSTEM_PLATFORM == "win32"