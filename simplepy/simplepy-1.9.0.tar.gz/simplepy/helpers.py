# coding: utf-8
import os

from simplepy import IS_WINDOWS

if IS_WINDOWS:
    import winreg

import requests

from simplepy import IS_WINDOWS, logger, IS_LINUX
from simplepy.multi_download import StreamDown
from simplepy.utils import unzip_file, get_cmd_print


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
    if IS_WINDOWS:
        plat_name = "chromedriver_win32.zip"
    elif IS_LINUX:
        plat_name = 'chromedriver_linux64.zip'
    else:
        plat_name = 'chromedriver_mac64_m1.zip'
    download_info = list(
        filter(lambda x: x.get("name") == plat_name, get_base_chrome_driver(result))
    )[0]
    download_url = download_info.get('url')
    download_name = download_info.get('name')
    return download_url, download_name


def download_chrome_driver(path):
    download_url, download_name = get_chrome_driver()
    sd = StreamDown(download_url, download_name, path, 20)
    sd.multi_down()
    file_name = os.path.join(path, download_name)
    unzip_file(file_name, path)
    if not IS_WINDOWS:
        logger.info('可执行文件')
        os.system(f'chmod 777 {file_name}')


def get_chrome_version():
    """
    https://blog.csdn.net/sinat_41870148/article/details/109263847
    :return:
    """
    try:
        if IS_WINDOWS:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            chrome_version = winreg.QueryValueEx(key, 'version')[0]
            return chrome_version, chrome_version.split('.')[0]
        elif IS_LINUX:
            # linux Google Chrome 102.0.5005.61
            chrome_version = get_cmd_print('google-chrome --version').split()[-1]
            return chrome_version, chrome_version.split('.')[0]
        else:
            # mac os
            # https://superuser.com/questions/1144651/get-chrome-version-from-commandline-in-mac
            chrome_version = get_cmd_print(
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version'
            ).split()[-1]
            return chrome_version, chrome_version.split('.')[0]
    except Exception as e:
        logger.error("该操作系统未安装Chrome Browser", e)


if __name__ == '__main__':
    get_chrome_driver()
