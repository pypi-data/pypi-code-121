# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['open_gopro',
 'open_gopro.api',
 'open_gopro.ble',
 'open_gopro.ble.adapters',
 'open_gopro.demos',
 'open_gopro.proto',
 'open_gopro.wifi',
 'open_gopro.wifi.adapters']

package_data = \
{'': ['*']}

install_requires = \
['betterproto[compiler]',
 'bleak==0.14.2',
 'construct',
 'packaging>=21.3,<22.0',
 'protobuf',
 'pydocstyle>=6.1.1,<7.0.0',
 'requests',
 'rich',
 'typing-extensions',
 'wrapt']

entry_points = \
{'console_scripts': ['gopro-ble-write = open_gopro.demos.ble_write:main',
                     'gopro-demo = open_gopro.demos.demo:main',
                     'gopro-log-battery = open_gopro.demos.log_battery:main',
                     'gopro-photo = open_gopro.demos.photo:entrypoint',
                     'gopro-stream = open_gopro.demos.stream:main',
                     'gopro-video = open_gopro.demos.video:main',
                     'gopro-wifi = open_gopro.demos.connect_wifi:main']}

setup_kwargs = {
    'name': 'open-gopro',
    'version': '0.9.1',
    'description': 'Open GoPro API and Examples',
    'long_description': '# Open GoPro Python SDK\n\n<img alt="GoPro Logo" src="https://raw.githubusercontent.com/gopro/OpenGoPro/main/docs/assets/images/logos/logo.png" width="50%" style="max-width: 500px;"/>\n\n[![Build and Test](https://img.shields.io/github/workflow/status/gopro/OpenGoPro/Python%20SDK%20Testing?label=Build%20and%20Test)](https://github.com/gopro/OpenGoPro/actions/workflows/python_sdk_test.yml)\n[![Build Docs](https://img.shields.io/github/workflow/status/gopro/OpenGoPro/Python%20SDK%20Docs%20Build%20and%20Deploy?label=Docs)](https://github.com/gopro/OpenGoPro/actions/workflows/python_sdk_deploy_docs.yml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPI](https://img.shields.io/pypi/v/open-gopro)](https://pypi.org/project/open-gopro/)\n[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gopro/OpenGoPro/blob/main/LICENSE)\n![Coverage](https://raw.githubusercontent.com/gopro/OpenGoPro/main/demos/python/sdk_wireless_camera_control/docs/_static/coverage.svg)\n\nThis is a Python package that provides an interface for the user to exercise the Open GoPro Bluetooth Low\nEnergy (BLE) and Wi-Fi API\'s as well as install command line interfaces to take photos, videos, and view\nthe preview stream.\n\n-   Free software: MIT license\n-   Documentation: [View on Open GoPro](https://gopro.github.io/OpenGoPro/python_sdk/)\n-   View on [Github](https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control)\n\n## Documentation\n\n> Note! This README is only an overview of the package.\n\nComplete documentation can be found on [Open GoPro](https://gopro.github.io/OpenGoPro/python_sdk/)\n\n## Features\n\n-   Top-level GoPro class interface to use both BLE / WiFi\n-   Cross-platform (tested on MacOS Big Sur, Windows 10, and Ubuntu 20.04)\n    -   BLE implemented using [bleak](https://pypi.org/project/bleak/)\n    -   Wi-Fi controller provided in the Open GoPro package (loosely based on the [Wireless Library](https://pypi.org/project/wireless/)\n-   Supports all commands, settings, and statuses from the [Open GoPro API](https://gopro.github.io/OpenGoPro/)\n-   Supports all versions of the Open GoPro API\n-   Automatically handles connection maintenance:\n    -   manage camera ready / encoding\n    -   periodically sends keep alive signals\n-   Includes detailed logging for each module\n-   Includes demo scripts installed as command-line applications to show BLE and WiFi functionality\n    -   Take a photo\n    -   Take a video\n    -   View the live stream\n    -   Log the battery\n\n## Installation\n\n> Note! This package requires Python >= 3.8\n\n```console\n    $ pip install open-gopro\n```\n\n## Usage\n\nTo automatically connect to GoPro device via BLE and WiFI, set the preset, set video parameters, take a\nvideo, and download all files:\n\n```python\nimport time\nfrom open_gopro import GoPro, Params\n\nwith GoPro() as gopro:\n    gopro.ble_command.load_preset(Params.Preset.CINEMATIC)\n    gopro.ble_setting.resolution.set(Params.Resolution.RES_4K)\n    gopro.ble_setting.fps.set(Params.FPS.FPS_30)\n    gopro.ble_command.set_shutter(Params.Shutter.ON)\n    time.sleep(2) # Record for 2 seconds\n    gopro.ble_command.set_shutter(Params.Shutter.OFF)\n\n    # Download all of the files from the camera\n    media_list = [x["n"] for x in gopro.wifi_command.get_media_list().flatten\n    for file in media_list:\n        gopro.wifi_command.download_file(camera_file=file)\n```\n\nAnd much more!\n\n## Demos\n\n> Note! These demos can be found on [Github](https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control/open_gopro/demos)\n\nDemos can be found in the installed package in the "demos" folder. They are installed as a CLI entrypoint\nand can be run via:\n\nCapture a photo and download it to your computer:\n\n```bash\n$ gopro-photo\n```\n\nCapture a video and download it to your computer:\n\n```bash\n$ gopro-video\n```\n\nStart the preview stream and view it with [VLC](https://www.videolan.org/):\n\n```bash\n$ gopro-stream\n```\n\nConnect to the GoPro and log battery consumption in to a .csv:\n\n```bash\n$ gopro-log-battery\n```\n\nConnect to the GoPro\'s Wi-Fi AP and maintain the connection:\n\n```bash\n$ gopro-wifi\n```\n\nFor more information on each, try running with help as such:\n\n```bash\n$ gopro-photo --help\n\nusage: gopro-photo [-h] [-i IDENTIFIER] [-l LOG] [-o OUTPUT] [-w WIFI_INTERFACE]\n\nConnect to a GoPro camera, take a photo, then download it.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -i IDENTIFIER, --identifier IDENTIFIER\n                        Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. If not used, first\n                        discovered GoPro will be connected to\n  -l LOG, --log LOG     Location to store detailed log\n  -o OUTPUT, --output OUTPUT\n                        Where to write the photo to. If not set, write to \'photo.jpg\'\n  -w WIFI_INTERFACE, --wifi_interface WIFI_INTERFACE\n                        System Wifi Interface. If not set, first discovered interface will be used.\n```\n',
    'author': 'Tim Camise',
    'author_email': 'tcamise@gopro.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gopro/OpenGoPro/tree/main/demos/python/sdk_wireless_camera_control',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
