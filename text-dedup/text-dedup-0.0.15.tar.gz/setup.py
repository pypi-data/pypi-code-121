# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['text_dedup', 'text_dedup.embedders', 'text_dedup.utils']

package_data = \
{'': ['*']}

install_requires = \
['annoy>=1.17.0,<2.0.0',
 'datasets>=2.2.2,<3.0.0',
 'datasketch>=1.5.7,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'mpire>=2.3.5,<3.0.0',
 'nltk>=3.7,<4.0',
 'numpy==1.22.3',
 'pandas>=1.4.2,<2.0.0',
 'scipy==1.7.3',
 'sentencepiece>=0.1.96,<0.2.0',
 'simhash>=2.1.2,<3.0.0',
 'torch>=1.11.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'transformers>=4.19.2,<5.0.0',
 'typer>=0.4.1,<0.5.0']

setup_kwargs = {
    'name': 'text-dedup',
    'version': '0.0.15',
    'description': '',
    'long_description': None,
    'author': 'Chenghao Mou',
    'author_email': 'mouchenghao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
