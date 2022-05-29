# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openpack_torch',
 'openpack_torch.data',
 'openpack_torch.models',
 'openpack_torch.models.imu',
 'openpack_torch.models.keypoint']

package_data = \
{'': ['*']}

install_requires = \
['hydra-core>=1.2.0,<2.0.0',
 'numpy<1.22.0',
 'omegaconf>=2.2.1,<3.0.0',
 'openpack-toolkit>=0.2.0,<0.3.0',
 'pandas>=1.2.4,<2.0.0',
 'pytorch-lightning>=1.6.3,<2.0.0',
 'sklearn>=0.0',
 'torch>=1.9.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'openpack-torch',
    'version': '0.1.0',
    'description': 'PyTorch extention to work around with OpenPack dataset',
    'long_description': '# openpack-torch\n\nPyTorch utilities to work around with OpenPack Dataset.\n\n## Setup\n\nYou can install via pip with the following command.\n\n```bash\n# Pip\npip install openpack-toolkit\n\n# Poetry\npoetry add  openpack-toolkit\n```\n\n## Docs\n\n- [Dataset Page](https://open-pack.github.io/)\n- API Docs (Comming soon...)\n\n## Examples\n\n### Work Step Recognition (Segmentation)\n\n#### IMU\n\n- Acceleration\n  - [U-Net](./examples/unet/) (Coming soon...)\n\n#### Vision\n\n- Keypoints\n  - [ST-GCN](./examples/st-gcn)  (Coming soon...)\n\n## LICENCE\n\n[MIT Licence](./LICENSE)\n',
    'author': 'Yoshimura Naoya',
    'author_email': 'yoshimura.naoya@ist.osaka-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://open-pack.github.io/home',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.11,<3.10',
}


setup(**setup_kwargs)
