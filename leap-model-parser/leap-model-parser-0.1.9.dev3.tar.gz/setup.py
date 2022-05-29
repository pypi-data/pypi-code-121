# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leap_model_parser',
 'leap_model_parser.contract',
 'leap_model_parser.utils',
 'leap_model_parser.utils.layerpedia',
 'leap_model_parser.utils.tlinspection',
 'leap_model_parser.utils.uicomponents']

package_data = \
{'': ['*']}

install_requires = \
['keras-data-format-converter==0.0.10',
 'numpy>=1.22.3,<2.0.0',
 'onnx2kerastl==0.0.34',
 'onnx>=1.11.0,<2.0.0',
 'tensorflow>=2.8,<3.0']

entry_points = \
{'console_scripts': ['update_ui_components = '
                     'scripts.scripts:update_ui_components']}

setup_kwargs = {
    'name': 'leap-model-parser',
    'version': '0.1.9.dev3',
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
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
