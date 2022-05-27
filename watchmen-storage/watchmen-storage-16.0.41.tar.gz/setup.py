# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_storage']

package_data = \
{'': ['*']}

install_requires = \
['watchmen-model==16.0.41']

setup_kwargs = {
    'name': 'watchmen-storage',
    'version': '16.0.41',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
