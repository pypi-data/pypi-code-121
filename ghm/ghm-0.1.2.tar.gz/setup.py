# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ghm']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0', 'pygit2>=1.9,<2.0']

entry_points = \
{'console_scripts': ['ghm = ghm.cli:main']}

setup_kwargs = {
    'name': 'ghm',
    'version': '0.1.2',
    'description': 'GitHub Mirrorer - Bulk mirror GitHub repositories',
    'long_description': None,
    'author': 'Mike Conigliaro',
    'author_email': 'mike@conigliaro.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mconigliaro/ghm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
