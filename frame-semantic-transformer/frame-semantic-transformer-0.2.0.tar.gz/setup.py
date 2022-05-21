# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['frame_semantic_transformer',
 'frame_semantic_transformer.data',
 'frame_semantic_transformer.data.augmentations',
 'frame_semantic_transformer.data.tasks']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.7,<4.0',
 'pytorch-lightning>=1.6.2,<2.0.0',
 'sentencepiece>=0.1.96,<0.2.0',
 'torch>=1.11.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'transformers==4.18.0']

setup_kwargs = {
    'name': 'frame-semantic-transformer',
    'version': '0.2.0',
    'description': 'Frame Semantic Parser based on T5 and FrameNet',
    'long_description': None,
    'author': 'David Chanin',
    'author_email': 'chanindav@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chanind/frame-semantic-transformer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
