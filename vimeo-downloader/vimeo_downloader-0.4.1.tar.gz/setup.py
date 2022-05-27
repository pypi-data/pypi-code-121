# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vimeo_downloader']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'tqdm>=4.62.3,<5.0.0']

extras_require = \
{':python_version >= "3.10" and python_version < "4"': ['urllib3>=1.26']}

setup_kwargs = {
    'name': 'vimeo-downloader',
    'version': '0.4.1',
    'description': 'Download videos and retrieve metadata from Vimeo.',
    'long_description': '# Vimeo Downloader  <!-- omit in toc -->\n\n[![PyPI](https://img.shields.io/pypi/v/vimeo_downloader?color=blue)](https://pypi.org/project/vimeo-downloader/)\n![PyPI - License](https://img.shields.io/pypi/l/vimeo_downloader?color=blue)\n\nDownloads Vimeo videos and retrieve metadata such as views, likes, comments, duration of the video.\n\n* [Features](#features)\n* [Installation](#installation)\n* [Usage](#usage)\n    - [Metadata](#metadata)\n    - [Download video](#download-video)\n    - [Download embed only videos](#downloading-embed-only-videos)\n    - [Downloading videos that require login](#downloading-videos-that-require-login)\n    - [Download with video ID](#download-video-with-video-id)\n* [Examples](#examples)\n\n# Features\n\n* Easy to use and friendly API.\n* Support for downloading private or embed only Vimeo videos.\n* Retrieve direct(.mp4 file) URL for the video.\n* Uses type-hints for better editor autocompletion\n* Retrieve metadata such as views, likes, comments, duration of the video\n* Tested for python 3.6 and above\n\n# Installation\n\n```bash\npip install vimeo_downloader\n```\n\nor download the latest version:\n\n```bash\npip install git+https://github.com/yashrathi-git/vimeo_downloader\n```\n\n# Usage\n\n```python\n>> from vimeo_downloader import Vimeo\n>> v = Vimeo(\'https://vimeo.com/503166067\')\n```\n\n## Metadata\n\n```python\n>> meta = v.metadata\n>> meta.title\n"We Don\'t Have To Know - Keli Holiday"\n>> meta.likes\n214\n>> meta.views\n8039\n>> meta._fields  # List of all meta data fields\n(\'id\', \'title\', \'description\'...)  # Truncated for readability\n```\n\n## Download video\n\n```python\n>> s = v.streams\n>> s\n[Stream(240p), Stream(360\np), Stream(540\np), Stream(720\np), Stream(1080\np)]\n>> best_stream = s[-1]  # Select the best stream\n>> best_stream.filesize\n\'166.589421 MB\'\n>> best_stream.direct_url\n\'https://vod-progressive.akamaized.net.../2298326263.mp4\'\n>> best_stream.download(download_directory=\'DirectoryName\',\n                        filename=\'FileName\')\n# Download video with progress bar and other information,\n# to disable this behaviour use mute=True\n```\n\n## Downloading embed only videos\n\n```python\n>> from vimeo_downloader import Vimeo\n>> v = Vimeo(\'https://player.vimeo.com/video/498617513\',\n             embedded_on=\'https://atpstar.com/plans-162.html\') \n```\n\nFor embed only videos, also provide embedded_on parameter to specify the URL on which video is embedded without query\nparameters.\n\n```python\n>> v.streams\n[Stream(240p), Stream(360\np), Stream(540\np), Stream(720\np), Stream(1080\np)]\n>> v.streams[-1].download(download_directory=\'DirectoryName\',\n                          filename=\'FileName\')\n# Downloads the best stream with progress bar and other information, \n# to disable this behaviour use mute=True\n```\n\n## Downloading videos that require login\n\n**It uses cookie to authenticate. You could get cookie like this:**\n\nWhile logged into your account, go to the video URL. Press Command + Shift + C or Control + Shift + C to get to\ndeveloper tools. Go to network tab and reload the page. You would see all requests that were made. Click on the top\none (request made to same URL you\'re on) and scroll down to "Request Headers", there you would find cookie parameter,\ncopy its value.\n\n```python\nfrom vimeo_downloader import Vimeo\n\ncookies = """\n    cookie\n """.strip()\n\nv = Vimeo(\n    url="URL",\n    cookies=cookies,\n)\n\nbest_stream = v.best_stream\nmp4_url = best_stream.direct_url\n\ntitle = best_stream.title\n\n## Download\nbest_stream.download()\n```\n\n## Download video with video ID\n\n(New in 0.3.2)\nIf the above methods, don\'t work it, you would most likely be able to download video using its vimeo video ID.\n\n```python\nfrom vimeo_downloader import Vimeo\n\n# url: https://vimeo.com/79761619\n# video ID: \'79761619\'\nv = Vimeo.from_video_id(video_id=\'79761619\')\n```\n\n# Examples\n\n## 1. Downloading embed only videos\n\n`embedded_on` is the URL of site video is embedded on without query parameters.\n\n```python\nfrom vimeo_downloader import Vimeo\n\n# Replace these two variables to different URL to download that video\nvimeo_url = \'https://player.vimeo.com/video/498617513\'\nembedded_on = \'https://atpstar.com/plans-162.html\'\n# embedded_on is  the URL of site video is embedded on without query parameters.\n\nv = Vimeo(vimeo_url, embedded_on)\n\nstream = v.streams  # List of available streams of different quality\n# >> [Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]\n\n# Download best stream\nstream[-1].download(download_directory=\'video\', filename=\'test_stream\')\n\n# Download video of particular quality, example \'540p\'\nfor s in stream:\n    if s.quality == \'540p\':\n        s.download(download_directory=\'video\', filename=\'test_stream\')\n        break\nelse:  # If loop never breaks\n    print("Quality not found")\n```\n\n## 2. Downloading a list of videos\n\n```python\nfrom vimeo_downloader import Vimeo\n\n# Replace these with other list of videos you want to download\nvideos = [\'https://vimeo.com/440801455\',\n          \'https://vimeo.com/504420495\',\n          \'https://vimeo.com/481277944\']\n\nfor video in videos:\n    v = Vimeo(video)\n    stream = v.streams  # List of available streams of different quality\n\n    # Selecting and downloading \'720p\' video\n    for s in stream:\n        if s.quality == \'720p\':\n            s.download(download_directory=\'video\', filename=v.metadata.title)\n            break\n    else:  # If the loop never break\n        print(\'quality not found\')\n```\n\n# License\n\nDistributed under the MIT licence. Read `LICENSE` for more information\nhttps://github.com/yashrathi-git/vimeo_downloader/blob/main/LICENCE\n\n',
    'author': 'Yash Rathi',
    'author_email': 'yashrathicricket@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yashrathi-git/vimeo_downloader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
