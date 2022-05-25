# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dai_python_commons']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.18.31,<2.0.0', 'loguru>=0.5.3,<0.6.0']

extras_require = \
{'data-consolidation': ['pyarrow==3.0.0', 's3fs==0.4.2']}

setup_kwargs = {
    'name': 'dai-python-commons',
    'version': '4.0.4',
    'description': 'Collection of small python utilities useful for lambda functions or glue jobs. By the Stockholm Public Transport Administration.',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
