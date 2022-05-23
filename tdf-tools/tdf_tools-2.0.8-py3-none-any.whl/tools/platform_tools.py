from enum import Enum
import os
import platform


class Platform(Enum):
    MACOS = 1
    WINDOWS = 2
    LINUX = 3


class PlatformTools:
    def pwd_cmd() -> str:
        if PlatformTools.is_windows():
            return "cd"
        else:
            return "pwd"

    def is_windows() -> bool:
        return PlatformTools.platform() == Platform.WINDOWS

    def platform():
        if platform.system().lower() == "windows":
            return Platform.WINDOWS
        elif platform.system().lower() == "macos":
            return Platform.MACOS
        elif platform.system().lower() == "linux":
            return Platform.LINUX
        else:
            return Platform.MACOS

    # 获取当前目录
    def curPath():
        cmd = "pwd"
        mPlatform = PlatformTools.platform()
        if mPlatform == Platform.WINDOWS:
            cmd = "cd"

        return os.popen(cmd).read().split("\n")[0]
