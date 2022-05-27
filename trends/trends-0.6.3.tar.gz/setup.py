# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trends', 'trends.docs.source']

package_data = \
{'': ['*'], 'trends': ['docs/*'], 'trends.docs.source': ['notebooks/*']}

install_requires = \
['nbsphinx>=0.8.8,<0.9.0']

setup_kwargs = {
    'name': 'trends',
    'version': '0.6.3',
    'description': 'Generate and study quasi-monotonic sequences.',
    'long_description': None,
    'author': 'Jeffrey S. Haemer',
    'author_email': 'jeffrey.haemer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
