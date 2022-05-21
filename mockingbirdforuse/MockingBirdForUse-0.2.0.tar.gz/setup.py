# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mockingbirdforuse',
 'mockingbirdforuse.encoder',
 'mockingbirdforuse.synthesizer',
 'mockingbirdforuse.synthesizer.models',
 'mockingbirdforuse.synthesizer.utils',
 'mockingbirdforuse.vocoder',
 'mockingbirdforuse.vocoder.hifigan',
 'mockingbirdforuse.vocoder.wavernn',
 'mockingbirdforuse.vocoder.wavernn.models']

package_data = \
{'': ['*']}

install_requires = \
['Unidecode>=1.3.0,<2.0.0',
 'inflect>=5.6.0,<6.0.0',
 'librosa>=0.9.0,<0.10.0',
 'loguru>=0.6.0,<0.7.0',
 'numba>=0.55.0,<0.56.0',
 'numpy>=1.19.0,<2.0.0',
 'pypinyin>=0.46.0,<0.47.0',
 'scipy>=1.8.0,<2.0.0',
 'torch>=1.11.0,<2.0.0',
 'webrtcvad>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'mockingbirdforuse',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
