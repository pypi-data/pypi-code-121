# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lgg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lgg',
    'version': '0.2.0',
    'description': 'A simple yet fancy logger for Python scripts',
    'long_description': "# python-logger\nA simple yet fancy logger for Python scripts\n\n## Install\n- Using pip:\n```shell\npip install lgg\n```\n\n- Using Poetry:\n```shell\npoetry add lgg\n```\n\n## Usage\n```python\n# This way\nfrom lgg import logger\n# Or\nfrom lgg import get_logger\nlogger = get_logger()\n# End Or\n\nlogger.info('This is an info message')\n\nlogger.debug('Debugging message')\n\nlogger.error('error message')\n\nlogger.warning('File not found! An empty one is created')\n```\n![Result](.resources/nameless.png)\n\n```python\nfrom lgg import get_logger\nlogger = get_logger('python-logger')\n\nlogger.info('This is an info message')\n\nlogger.debug('Debugging message')\n\nlogger.error('error message')\n\nlogger.warning('File not found! An empty one is created')\n```\n![Result](.resources/python-logger.png)\n\n**Notice the change after each log's datetime, the former shows the filename and line of code,\nthe latter displays the logger name instead**\n",
    'author': 'Ayoub Assis',
    'author_email': 'assis.ayoub@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blurry-mood/python-logger',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
