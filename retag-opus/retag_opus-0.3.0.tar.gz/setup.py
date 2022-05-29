# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['retag_opus']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0',
 'mutagen>=1.45.1,<2.0.0',
 'shtab>=1.5.4,<2.0.0',
 'simple-term-menu>=1.4.1,<2.0.0']

entry_points = \
{'console_scripts': ['retag = retag_opus.app:run']}

setup_kwargs = {
    'name': 'retag-opus',
    'version': '0.3.0',
    'description': 'An app to tag music files downloaded from Youtube with all the information available in the Youtube description.',
    'long_description': None,
    'author': 'Simon Bengtsson',
    'author_email': 'gevhaz@tutanota.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
