# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logging_utils_tddschn']

package_data = \
{'': ['*']}

install_requires = \
['utils-tddschn>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'logging-utils-tddschn',
    'version': '0.1.9',
    'description': 'Logging utilities for personal use.',
    'long_description': "# logging-utils-tddschn\n\nLogging utilities for personal use.\n\n- [logging-utils-tddschn](#logging-utils-tddschn)\n\t- [Install](#install)\n\t- [Example Usage](#example-usage)\n\t\t- [`get_logger`](#get_logger)\n## Install\n```\n$ pip install logging-utils-tddschn\n```\n\n## Example Usage\n\n### [`get_logger`](logging_utils_tddschn/utils.py)\n\nCheck the source code linked above to learn more about the arguments.\n\n```python\nfrom logging_utils_tddschn import get_logger\n\nlogger, _ = get_logger(__name__)\nlogger.info('Logging from logging-utils-tddschn!')\n```\n\n```\n_DEBUG=1 python3 app.py\n# prints something like\n# INFO:tests.test_utils_naive:/Users/tddschn/app.py:5:my_func:Logging from logging-utils-tddschn!\n\n# logging is turned off (sent to NullHandler) if you don't set env var _DEBUG or it's set to false.\n```\n\n",
    'author': 'Xinyuan Chen',
    'author_email': '45612704+tddschn@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tddschn/logging-utils-tddschn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
