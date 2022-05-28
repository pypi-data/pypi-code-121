import os
import winreg

import requests
from simplepy.multi_download import StreamDown
from simplepy import IS_WINDOWS, logger
from simplepy.utils import unzip_file


def get_base_chrome_driver(version):
    data = [
        {
            "name": "chromedriver_linux64.zip",
            "url": f"https://registry.npmmirror.com/-/binary/chromedriver/{version}chromedriver_linux64.zip",
        },
        {
            "name": "chromedriver_mac64.zip",
            "url": f"https://registry.npmmirror.com/-/binary/chromedriver/{version}chromedriver_mac64.zip",
        },
        {
            "name": "chromedriver_mac64_m1.zip",
            "url": f"https://registry.npmmirror.com/-/binary/chromedriver/{version}chromedriver_mac64_m1.zip",
        },
        {
            "name": "chromedriver_win32.zip",
            "url": f"https://registry.npmmirror.com/-/binary/chromedriver/{version}chromedriver_win32.zip",
        }
    ]
    return data


def get_chrome_driver():
    html = requests.get('https://registry.npmmirror.com/-/binary/chromedriver/').json()
    main_version = get_chrome_version()[1]
    result = list(filter(lambda x: str(x.get('name')).startswith(main_version), html))[0].get('name')
    download_info = list(
        filter(lambda x: x.get("name") == "chromedriver_win32.zip", get_base_chrome_driver(result))
    )[0]
    download_url = download_info.get('url')
    download_name = download_info.get('name')
    return download_url, download_name


def download_chrome_driver(path):
    download_url, download_name = get_chrome_driver()
    sd = StreamDown(download_url, download_name, path)
    sd.multi_down()
    file_name = os.path.join(path, download_name)
    unzip_file(file_name, path)


def get_chrome_version():
    try:
        if IS_WINDOWS:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            chrome_version = winreg.QueryValueEx(key, 'version')[0]
            return chrome_version, chrome_version.split('.')[0]
        else:
            os.system('google-chrome --version')
    except Exception as e:
        logger.error("该操作系统未安装Chrome Browser", e)


if __name__ == '__main__':
    get_chrome_driver()
