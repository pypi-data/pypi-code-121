# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aitg', 'aitg.gens', 'aitg.models']

package_data = \
{'': ['*']}

install_requires = \
['aitextgen>=0.5.2,<0.6.0',
 'bottle>=0.12.19,<0.13.0',
 'colorama>=0.4.4,<0.5.0',
 'loguru>=0.6.0,<0.7.0',
 'lz4>=4.0.0,<5.0.0',
 'msgpack>=1.0.2,<2.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'single-source>=0.3.0,<0.4.0',
 'torch>=1.11.0,<2.0.0',
 'transformers>=4.18.0,<5.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['aitg_download_model = aitg.model:download_model_main',
                     'aitg_gpt_cli = aitg.gpt_cli:main',
                     'aitg_srv = aitg.srv:main',
                     'aitg_t5_cli = aitg.t5_cli:main']}

setup_kwargs = {
    'name': 'aitg',
    'version': '3.4.0',
    'description': 'aitg is a multitool for working with transformer models',
    'long_description': None,
    'author': 'redthing1',
    'author_email': 'redthing1@alt.icu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
