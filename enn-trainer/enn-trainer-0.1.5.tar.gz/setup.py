# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enn_trainer', 'enn_trainer.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0',
 'entity-gym>=0.1.2,<0.2.0',
 'hyperstate>=0.3.9,<0.4.0',
 'moviepy>=1.0.3,<2.0.0',
 'msgpack-numpy>=0.4.7,<0.5.0',
 'msgpack>=1.0.3,<2.0.0',
 'numpy>=1.21.4,<2.0.0',
 'optuna>=2.10.0,<3.0.0',
 'ragged-buffer>=0.3.9,<0.4.0',
 'rogue-net>=0.1.3,<0.2.0',
 'tensorboard>=2.7.0,<3.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'wandb>=0.12.7,<0.13.0']

setup_kwargs = {
    'name': 'enn-trainer',
    'version': '0.1.5',
    'description': 'PPO and supervised training loops compatible with entity-gym',
    'long_description': None,
    'author': 'Clemens Winter',
    'author_email': 'clemenswinter1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
