# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orkgnlp',
 'orkgnlp.annotation',
 'orkgnlp.annotation.csner',
 'orkgnlp.annotation.csner._ncrfpp',
 'orkgnlp.annotation.csner._ncrfpp.model',
 'orkgnlp.annotation.csner._ncrfpp.utils',
 'orkgnlp.clustering',
 'orkgnlp.common',
 'orkgnlp.common.config',
 'orkgnlp.common.tools',
 'orkgnlp.common.util']

package_data = \
{'': ['*']}

install_requires = \
['huggingface-hub>=0.5.1,<0.6.0',
 'nltk==3.5',
 'numpy==1.21.6',
 'onnx==1.11.0',
 'onnxruntime==1.11.1',
 'pandas==1.3.5',
 'spacy==3.3.0',
 'torch==1.11.0']

setup_kwargs = {
    'name': 'orkgnlp',
    'version': '0.2.1',
    'description': 'Python package wrapping the ORKG NLP Services.',
    'long_description': '# ORKG NLP PyPI\n[![Documentation Status](https://readthedocs.org/projects/orkg-nlp-pypi/badge/?version=latest)](https://orkg-nlp-pypi.readthedocs.io/en/latest/?badge=latest)\n[![PyPI version](https://badge.fury.io/py/orkgnlp.svg)](https://badge.fury.io/py/orkgnlp)\n\nPyPI package wrapping the ORKG NLP services.\n\nCheck our [Read the Docs](https://orkg-nlp-pypi.readthedocs.io/en/latest/) for more details!',
    'author': 'Omar Arab Oghli',
    'author_email': 'omar.araboghli@outlook.com',
    'maintainer': 'Omar Arab Oghli',
    'maintainer_email': None,
    'url': 'http://orkg.org/about',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
