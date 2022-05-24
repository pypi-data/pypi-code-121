# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['texi',
 'texi.apps',
 'texi.apps.classification',
 'texi.apps.ner',
 'texi.apps.text_matching',
 'texi.datasets',
 'texi.pytorch',
 'texi.pytorch.dataset',
 'texi.pytorch.metrics',
 'texi.pytorch.models',
 'texi.pytorch.models.spert',
 'texi.tagger']

package_data = \
{'': ['*'], 'texi.apps.ner': ['templates/*']}

install_requires = \
['numpy',
 'pandas',
 'plotly',
 'pyahocorasick',
 'pycarton',
 'pytorch-crf',
 'pytorch-ignite',
 'torch',
 'transformers']

setup_kwargs = {
    'name': 'texi',
    'version': '0.2.3',
    'description': 'Text processing toolbox.',
    'long_description': None,
    'author': 'Yevgnen Koh',
    'author_email': 'wherejoystarts@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
