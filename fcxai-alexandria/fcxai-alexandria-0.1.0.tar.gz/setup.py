# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'alexandria'}

packages = \
['galib', 's3lib']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.21.16,<2.0.0',
 'google-analytics-data>=0.11.2,<0.12.0',
 'google-api-python-client>=2.47.0,<3.0.0',
 'joblib>=1.1.0,<2.0.0',
 'oauth2client==4.1.3',
 'pandas>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'fcxai-alexandria',
    'version': '0.1.0',
    'description': 'Everything for building and remodeling (your application) in one place',
    'long_description': '# AlexandrIA Libs\n\nEverything for building and remodeling (your application) in one place\n\n## Installation\n\n### Production env\n\n```bash\npip install git+https://git-codecommit.us-east-1.amazonaws.com/v1/repos/fcxlabs-alexandria\n```\n\n### Development\n\n```bash\npip install .\n```\n\n## Usage\n\nJust packages in `alexandria` folder are installed, not alexandria itself.\n\n```python\nimport galib as ga\nimport s3lib as s3\n```\n',
    'author': 'FCxLabs-AI',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
