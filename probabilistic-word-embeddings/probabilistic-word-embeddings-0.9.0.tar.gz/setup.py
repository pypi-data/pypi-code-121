# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['probabilistic_word_embeddings']

package_data = \
{'': ['*'], 'probabilistic_word_embeddings': ['data/eval/*']}

install_requires = \
['progressbar2', 'tensorflow-probability>=0.11,<0.12', 'tensorflow>=2.2,<3.0']

setup_kwargs = {
    'name': 'probabilistic-word-embeddings',
    'version': '0.9.0',
    'description': 'Probabilistic Word Embeddings for Python',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
