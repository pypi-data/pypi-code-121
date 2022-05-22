# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leap_model_parser', 'leap_model_parser.contract']

package_data = \
{'': ['*']}

install_requires = \
['keras-data-format-converter==0.0.8',
 'numpy>=1.22.3,<2.0.0',
 'onnx2kerastl==0.0.33.dev1',
 'onnx>=1.11.0,<2.0.0',
 'tensorflow>=2.8,<3.0']

setup_kwargs = {
    'name': 'leap-model-parser',
    'version': '0.1.7.dev3',
    'description': '',
    'long_description': '# Tensorleap model parser\nUsed to parse model to the import format \n',
    'author': 'idan',
    'author_email': 'idan.yogev@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tensorleap/leap-model-parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
