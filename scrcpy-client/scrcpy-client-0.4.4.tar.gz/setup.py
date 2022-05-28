# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scrcpy', 'scrcpy_ui']

package_data = \
{'': ['*']}

install_requires = \
['adbutils>=0.16.2,<0.17.0', 'av>=9.0.0,<10.0.0', 'opencv-python>=4.5.0,<5.0.0']

extras_require = \
{'ui': ['PySide6>=6.0.0,<7.0.0']}

entry_points = \
{'console_scripts': ['py-scrcpy = scrcpy_ui:main']}

setup_kwargs = {
    'name': 'scrcpy-client',
    'version': '0.4.4',
    'description': 'A client of scrcpy',
    'long_description': '# Python Scrcpy Client\n<p>\n    <a href="https://pypi.org/project/scrcpy-client/" target="_blank">\n        <img src="https://img.shields.io/pypi/v/scrcpy-client" />\n    </a>\n    <a href="https://github.com/leng-yue/py-scrcpy-client/actions/workflows/ci.yml" target="_blank">\n        <img src="https://img.shields.io/github/workflow/status/leng-yue/py-scrcpy-client/CI" />\n    </a>\n    <a href="https://app.codecov.io/gh/leng-yue/py-scrcpy-client" target="_blank">\n        <img src="https://img.shields.io/codecov/c/github/leng-yue/py-scrcpy-client" />\n    </a>\n    <img src="https://img.shields.io/github/license/leng-yue/py-scrcpy-client" />\n    <a href="https://pepy.tech/project/scrcpy-client" target="_blank">\n        <img src="https://pepy.tech/badge/scrcpy-client" />\n    </a>\n    <a href="https://github.com/Genymobile/scrcpy/tree/v1.20" target="_blank">\n        <img src="https://img.shields.io/badge/scrcpy-v1.20-violet" />\n    </a>\n</p>\n\nThis package allows you to view and control android device in realtime.\n\n![demo gif](https://raw.githubusercontent.com/leng-yue/py-scrcpy-client/main/demo.gif)  \n\nNote: This gif is compressed and experience lower quality than actual.\n\n## How to use\nTo begin with, you need to install this package via pip:\n```shell\npip install scrcpy-client[ui]\n```\nThen, you can start `py-scrcpy` to view the demo:\n\nNote: you can ignore `[ui]` if you don\'t want to view the demo ui\n\n## Document\nHere is the document GitHub page: [Documentation](https://leng-yue.github.io/py-scrcpy-client/)  \nAlso, you can check `scrcpy_ui/main.py` for a full functional demo.\n\n## Contribution & Development\nAlready implemented all functions in scrcpy server 1.20.  \nPlease check scrcpy server 1.20 source code: [Link](https://github.com/Genymobile/scrcpy/tree/v1.20/server)\n\n## Reference & Appreciation\n- Core: [scrcpy](https://github.com/Genymobile/scrcpy)\n- Idea: [py-android-viewer](https://github.com/razumeiko/py-android-viewer)\n- CI: [index.py](https://github.com/index-py/index.py)\n',
    'author': 'lengyue',
    'author_email': 'lengyue@lengyue.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/leng-yue/py-scrcpy-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
