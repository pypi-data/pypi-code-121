# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openpack_toolkit',
 'openpack_toolkit.activity',
 'openpack_toolkit.codalab',
 'openpack_toolkit.codalab.workprocess_segmentation']

package_data = \
{'': ['*']}

install_requires = \
['numpy<1.22.0', 'pandas>=1.2.4', 'pytest-cov>=3.0.0,<4.0.0', 'sklearn>=0.0']

setup_kwargs = {
    'name': 'openpack-toolkit',
    'version': '0.1.0',
    'description': 'Toolkit for OpenPack Dataset',
    'long_description': '# OpenPack Dataset Toolkit (optk)\n\n"OpenPack Dataset" is a new large-scale multi modal dataset of manual packing process.\nOpenPack is an open access logistics-dataset for human activity recognition, which contains human movement and package information from 17 distinct subjects.\nThis repository provide utilities to explore our exciting dataset.\n\n## Setup\n\nWe provide some utility functions as python package. You can install via pip with the following command.\n\n```bash\n# Pip\npip install openpack-toolkit\n\n# Poetry\npoetry add  openpack-toolkit\n```\n\n## Documentation\n\n- [Dataset Page](https://open-pack.github.io/)\n- API Docs (Comming soon...)\n\n## Examples\n\n- ST-GCN with Keypoints Data (TBA)\n- U-Net with Accelration Data\n',
    'author': 'Yoshimura Naoya',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://open-pack.github.io/home',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.11,<3.10',
}


setup(**setup_kwargs)
