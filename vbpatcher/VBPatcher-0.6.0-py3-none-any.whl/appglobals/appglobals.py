from datetime import datetime
import bs4
import requests as req
from requests import Response


def get_stable_assets(url: str, mode: int):
    """Send GET request to retrieve BepInEx stable release assets, depending on value passed to :param:`mode`.

    - If :param:`mode` set to 1, get patch archive download link.
    - If :param:`mode` set to 2, get patch release version.

    ---

    :param url: URL for the new :class:`Request` object.
    :type url: :class:`str` | :class:`PathLike`
    :param mode: specifies values to retrieve from response.
    :type mode: :class:`int`
    :return: response content from GET request.
    :rtype: :class:`str` | None
    """
    r: Response = req.get(url, 'html.parser')
    r.raise_for_status()

    dl_link: str = r.json()['assets'][1]['browser_download_url']
    patch_ver: str = r.json()['assets'][1]['name'][12:20]

    if mode == 1:
        return dl_link
    if mode == 2:
        return patch_ver


def get_dev_assets(url: str, mode: int):
    """Send GET request to retrieve BepInEx dev/bleeding-edge release assets, depending on value passed to :param:`mode`.

    - If :param:`mode` set to 1, get patch archive download link.
    - If :param:`mode` set to 2, get patch version.

    ---

    :param url: URL for the new :class:`Request` object.
    :type url: :class:`str` | :class:`PathLike`
    :param mode: specifies values to retrieve from response.
    :type mode: :class:`int`
    :return: response content from GET request.
    :rtype: :class:`str` | None
    """
    retrieved = 0

    r: Response = req.get(url)
    r.raise_for_status()

    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    results = soup.find_all('div', class_="artifacts-list")

    for result in results:
        if retrieved < 1:
            link = result.find_all('a')[0]['href']
            retrieved += 1

    dl_link = (f'{url[:26]}{link}')

    if mode == 1:
        return dl_link
    elif mode == 2:
        return dl_link[73:80]


p_stable: str = r'.\patch-files\stable'  # Stable patch file location
url_stable = get_stable_assets(
    'http://api.github.com/repos/BepInEx/BepInEx/releases/latest',
    1)  # stable release download link
b_stable = get_stable_assets(
    'http://api.github.com/repos/BepInEx/BepInEx/releases/latest',
    2)  # stable release version

p_dev: str = r'.\patch-files\development'  # Development patch file location
url_dev = get_dev_assets('https://builds.bepinex.dev/projects/bepinex_be',
                         1)  # dev/bleeding-edge build download link
b_dev: str = get_dev_assets('https://builds.bepinex.dev/projects/bepinex_be',
                            2)  # dev/bleeding-edge build number

p_targetDir: str = r'C:\Program Files (x86)\Steam\steamapps\common\Valheim'  # target directory to patch

_logFile: str = r'.\logs\patchLog.log'  # Log file location

_datefmt: str = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)  # Date and time format to display when starting program.

_textborder: str = "=".ljust((78),
                             "=")  # Text border for log file organization.
