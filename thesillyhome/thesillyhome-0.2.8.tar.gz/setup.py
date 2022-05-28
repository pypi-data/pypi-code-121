# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['thesillyhome', 'thesillyhome.model_creator']

package_data = \
{'': ['*']}

install_requires = \
['appdaemon>=4.2.1,<5.0.0',
 'joblib==1.1.0',
 'mysql-connector==2.2.9',
 'tqdm==4.64.0']

setup_kwargs = {
    'name': 'thesillyhome',
    'version': '0.2.8',
    'description': '',
    'long_description': None,
    'author': 'Chrisopher Lai',
    'author_email': None,
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
