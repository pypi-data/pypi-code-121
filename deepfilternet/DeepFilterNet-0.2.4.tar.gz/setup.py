# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['df', 'df.scripts']

package_data = \
{'': ['*']}

install_requires = \
['deepfilterlib==0.2.4',
 'loguru>=0.5',
 'numpy>=1.20,<2.0',
 'typing_extensions>=4.0,<5.0']

extras_require = \
{'dnsmos': ['requests>=2.27,<3.0'],
 'dnsmos-local': ['requests>=2.27,<3.0',
                  'appdirs>=1.4,<2.0',
                  'onnxruntime>=1.11,<2.0'],
 'eval': ['pystoi>=0.3,<0.4', 'pesq>=0.0.3,<0.0.4', 'scipy>=1,<2'],
 'soundfile': ['soundfile>=0.10,<0.11'],
 'train': ['deepfilterdataloader==0.2.4', 'icecream>=2,<3']}

entry_points = \
{'console_scripts': ['deepFilter = df.enhance:run']}

setup_kwargs = {
    'name': 'deepfilternet',
    'version': '0.2.4',
    'description': 'Noise supression using deep filtering',
    'long_description': None,
    'author': 'Hendrik Schröter',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Rikorose/DeepFilterNet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
