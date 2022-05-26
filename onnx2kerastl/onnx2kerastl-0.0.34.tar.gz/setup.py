# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onnx2kerastl', 'onnx2kerastl.customonnxlayer']

package_data = \
{'': ['*']}

install_requires = \
['onnx>=1.11.0,<2.0.0',
 'tensorflow-addons>=0.16.1,<0.17.0',
 'tensorflow>=2.8,<3.0']

setup_kwargs = {
    'name': 'onnx2kerastl',
    'version': '0.0.34',
    'description': '',
    'long_description': None,
    'author': 'dorhar',
    'author_email': 'doron.harnoy@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
