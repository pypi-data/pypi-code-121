
from typing import NamedTuple


DEFAULT_USER_AGENT_ANDROID = (
    "Mozilla/5.0 (Linux; Android 9; Redmi Note 7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/83.0.4103.106 Mobile Safari/537.36"
)
DEFAULT_USER_AGENT_IOS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
)
DEFAULT_USER_AGENT_HUAWEI = (
    "Mozilla/5.0 (Linux; Android 8.1; EML-L29 Build/HUAWEIEML-L29; xx-xx) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 "
    "Mobile Safari/537.36"
)


class DesktopDevice(NamedTuple):
    width: int
    height: int
    user_agent: str = ''


class MobileDevice(NamedTuple):
    """
    Mobile device only can be chosen from list of known devices is generated
    from those found in the DevTools Emulation panel in Chrome Browser

    For example: "Nexus 5", "Galaxy S5", "iPhone X"

    More info: https://chromedriver.chromium.org/mobile-emulation

    Usage:
        NEXUS_5 = MobileDevice("Nexus 5")
    """
    device_name: str


class CustomDevice(NamedTuple):
    """
    It is possible to create your own device,
    which is not in the list of known devices in DevTools Emulator panel

    Usage:
        XIAOMI_REDMI_7 = CustomDevice(393, 851)
    """
    width: int
    height: int
    pixel_ratio: float = 1.0
    user_agent: str = DEFAULT_USER_AGENT_ANDROID


CHROME_DESKTOP_1920_1080 = DesktopDevice(1920, 1080)
CHROME_DESKTOP_1024_768 = DesktopDevice(1024, 768)

ANDROID_360_640 = CustomDevice(360, 640, 3.0)
ANDROID_1280_800 = CustomDevice(1280, 800, 3.0)
XIAOMI_REDMI_7 = CustomDevice(393, 851)

HUAWEI_P20 = CustomDevice(768, 850, 3.0, DEFAULT_USER_AGENT_HUAWEI)

IOS_750_1334 = CustomDevice(750, 1334, 2.0, DEFAULT_USER_AGENT_IOS)
IOS_1080_1920 = CustomDevice(1080, 1920, 2.0, DEFAULT_USER_AGENT_IOS)

NEXUS_5 = MobileDevice("Nexus 5")

IPHONE_X = MobileDevice("iPhone X")
IPAD_MINI = MobileDevice("iPad Mini")
IPAD_PRO = MobileDevice("iPad Pro")
